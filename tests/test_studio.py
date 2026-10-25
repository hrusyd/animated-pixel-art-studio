import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pixel_studio", ROOT / "skills/animated-pixel-art-studio/scripts/studio.py")
studio = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(studio)


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scene = {"version":1,"name":"Test","canvas":[8,8],"fps":12,"frames":12,"scale":2,
                      "palette":{"0":"#111827","a":"#f8e8c8"},"background":"0",
                      "sprites":{"dot":{"rows":["a.","aa"]}},
                      "layers":[{"sprite":"dot","motion":{"keys":[[0,0,2],[6,5,2],[12,0,2]]}}]}

    def write(self, data=None):
        path = self.root / "scene.json"
        path.write_text(json.dumps(self.scene if data is None else data),encoding="utf-8")
        return path

    def test_all_presets_validate(self):
        for path in studio.ASSETS.glob("*.json"):
            with self.subTest(path=path.name):
                studio.load_scene(path)

    def test_motion_and_endpoint(self):
        layer = self.scene["layers"][0]
        self.assertEqual(studio.position(layer,0),(0,2))
        self.assertEqual(studio.position(layer,6),(5,2))
        self.assertEqual(studio.position(layer,12),(0,2))
        layer["motion"]["period"]=12
        self.assertEqual(studio.position(layer,13),studio.position(layer,1))

    def test_step_interpolation(self):
        layer=self.scene["layers"][0]
        layer["motion"]["interpolation"]="step"
        self.assertEqual(studio.position(layer,5),(0,2))
        self.assertEqual(studio.position(layer,6),(5,2))

    def test_transparency_layer_order_and_clipping(self):
        self.scene["layers"]=[{"rect":[8,8],"color":"a"},{"sprite":"dot","x":-1,"y":0}]
        data,pal,sprites=studio.load_scene(self.write())
        frame=studio.render_frame(data,pal,sprites,0)
        self.assertEqual(frame.getpixel((0,0)),pal["a"])
        self.assertEqual(frame.size,(8,8))

    def test_bad_palette_and_ragged_sprites(self):
        for rows in [["xx"],["aa","a"]]:
            self.scene["sprites"]["dot"]["rows"]=rows
            with self.assertRaises(studio.SceneError):studio.load_scene(self.write())

    def test_path_traversal_rejected(self):
        self.scene["sprites"]["dot"]={"image":"../outside.png"}
        with self.assertRaisesRegex(studio.SceneError,"escapes"):
            studio.load_scene(self.write())

    def test_png_palette_and_alpha(self):
        image=Image.new("RGBA",(2,2),(248,232,200,255))
        image.save(self.root/"sprite.png")
        self.scene["sprites"]["dot"]={"image":"sprite.png"}
        studio.load_scene(self.write())
        image.putpixel((0,0),(248,232,200,128));image.save(self.root/"sprite.png")
        with self.assertRaisesRegex(studio.SceneError,"binary alpha"):studio.load_scene(self.write())
        image.putpixel((0,0),(255,0,0,255));image.save(self.root/"sprite.png")
        with self.assertRaisesRegex(studio.SceneError,"outside scene palette"):studio.load_scene(self.write())

    def test_invalid_timing_and_fields(self):
        for key,value in [("fps",0),("frames",-1),("scale",1.5),("fps",True),("unknown",1)]:
            data=copy.deepcopy(self.scene);data[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(studio.SceneError):
                studio.load_scene(self.write(data))

    def test_bad_keys_and_animation(self):
        self.scene["layers"][0]["motion"]["keys"]=[[0,1,1],[0,2,2]]
        with self.assertRaises(studio.SceneError):studio.load_scene(self.write())
        self.scene["layers"]=[{"animation":[]}]
        with self.assertRaises(studio.SceneError):studio.load_scene(self.write())

    def test_visibility(self):
        self.scene["layers"][0]["visible"]=[2,4]
        data,pal,sprites=studio.load_scene(self.write())
        self.assertEqual(len(studio.render_frame(data,pal,sprites,0).getcolors()),1)
        self.assertEqual(len(studio.render_frame(data,pal,sprites,2).getcolors()),2)
        self.assertEqual(len(studio.render_frame(data,pal,sprites,4).getcolors()),1)

    def test_gif_centisecond_timing(self):
        for fps in [8,12,24,30,50]:
            ticks=studio.gif_durations(37,fps)
            self.assertTrue(all(n>=20 and n%10==0 for n in ticks))
            self.assertLessEqual(abs(sum(ticks)-37000/fps),5.01)

    def test_export_preserves_pixels_duration_and_source(self):
        path=self.write(); out=self.root/"render"
        report=studio.export(path,out,{"png","gif"})
        self.assertEqual(report["frames"],12)
        self.assertGreater(report["unique_frames"],1)
        self.assertEqual(len(list((out/"frames").glob("*.png"))),12)
        self.assertEqual(json.loads((out/"source/scene.json").read_text()),self.scene)
        with Image.open(out/"poster.png") as poster:
            self.assertEqual(poster.size,(16,16))
            self.assertEqual({c for _,c in poster.getcolors()}, {(17,24,39),(248,232,200)})
        with Image.open(out/"animation.gif") as gif:
            self.assertEqual(gif.info["loop"],0)
            duration=0
            for i in range(gif.n_frames):
                gif.seek(i);duration+=gif.info["duration"]
            self.assertEqual(duration,1000)
        second=studio.export(path,self.root/"second",{"gif"})
        self.assertEqual(report["frame_sha256"],second["frame_sha256"])

    def test_refuses_output_overwrite(self):
        output=self.root/"existing";output.mkdir();(output/"keep.txt").write_text("keep")
        with self.assertRaisesRegex(studio.SceneError,"empty"):
            studio.export(self.write(),output,{"gif"})
        self.assertEqual((output/"keep.txt").read_text(),"keep")

    def test_nonloop_gif(self):
        self.scene["loop"]=False
        studio.export(self.write(),self.root/"once",{"gif"})
        with Image.open(self.root/"once/animation.gif") as gif:
            self.assertNotIn("loop",gif.info)

    def test_imported_source_is_portable(self):
        (self.root/"sprites").mkdir()
        Image.new("RGBA",(2,2),(248,232,200,255)).save(self.root/"sprites/dot.png")
        self.scene["sprites"]["dot"]={"image":"sprites/dot.png"}
        report=studio.export(self.write(),self.root/"portable",{"gif"})
        copied=self.root/"portable/source/scene.json"
        self.assertTrue((copied.parent/"sprites/dot.png").is_file())
        second=studio.export(copied,self.root/"rerender",{"gif"})
        self.assertEqual(report["frame_sha256"],second["frame_sha256"])

    def test_installed_skill_runs_without_repo(self):
        destination=self.root/"installed"
        install=subprocess.run([sys.executable,str(ROOT/"tools/install_skill.py"),"--target",str(destination)],capture_output=True,text=True)
        self.assertEqual(install.returncode,0,install.stderr)
        script=destination/"animated-pixel-art-studio/scripts/studio.py"
        scene=self.root/"standalone.json"
        create=subprocess.run([sys.executable,str(script),"init","--preset","blank","--out",str(scene)],cwd=self.root,capture_output=True,text=True)
        self.assertEqual(create.returncode,0,create.stderr)
        render=subprocess.run([sys.executable,str(script),"render",str(scene),"--out",str(self.root/"standalone-render"),"--formats","gif"],cwd=self.root,capture_output=True,text=True)
        self.assertEqual(render.returncode,0,render.stderr)
        repeat=subprocess.run([sys.executable,str(ROOT/"tools/install_skill.py"),"--target",str(destination)],capture_output=True,text=True)
        self.assertEqual(repeat.returncode,2)

    def test_cli_validation_failure_is_nonzero(self):
        self.scene["fps"]=0
        result=subprocess.run([sys.executable,str(ROOT/"studio.py"),"validate",str(self.write())],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn("fps",result.stderr)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg/ffprobe not installed")
    def test_mp4_actual_metadata_and_odd_padding(self):
        self.scene["canvas"]=[9,7];self.scene["scale"]=1
        out=self.root/"video"
        studio.export(self.write(),out,{"mp4"})
        result=subprocess.run([shutil.which("ffprobe"),"-v","error","-select_streams","v:0","-show_entries","stream=width,height,nb_frames,r_frame_rate,duration","-of","json",str(out/"animation.mp4")],check=True,capture_output=True,text=True)
        stream=json.loads(result.stdout)["streams"][0]
        self.assertEqual((stream["width"],stream["height"]),(10,8))
        self.assertEqual(stream["nb_frames"],"12")
        self.assertEqual(stream["r_frame_rate"],"12/1")
        self.assertAlmostEqual(float(stream["duration"]),1,places=2)


if __name__ == "__main__":unittest.main()
