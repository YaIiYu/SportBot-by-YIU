import os
import re
import subprocess
import utils.decrement as re_functions
import moviepy as mp
from aiogram import types
from idna.idnadata import scripts


from data.schedule.day_schedule_handler import ScheduleDatabase

class Archive_Helper:
    def __init__(self):
        self.rel_path = os.path.dirname(__file__)
        #print(self.rel_path)
    def send_photo(self,filepath):
        #print(self.rel_path)
        return types.FSInputFile(str(os.path.join(self.rel_path,filepath)))

    def send_video(self, filepath):
        return types.FSInputFile(str(os.path.join(self.rel_path, filepath)))

    def video_compressor(self, input_path, output_path=None, crf=28, preset="slow"):
            ffmpeg_executable = os.path.join(self.rel_path,"FFMPEG\\bin\\ffmpeg.exe")
            if output_path is None:
                ip = input_path.split(".")
                output_path = ip[0] + "_compr" + "." + ip[1]
            input_path = str(os.path.join(self.rel_path, input_path))
            output_path = str(os.path.join(self.rel_path, output_path))
            print(f"InPath : {input_path};\nOutPath: {output_path}")
            cmd = [
                ffmpeg_executable, "-i", input_path,
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                "-vcodec", "libx264", "-crf", str(crf), "-preset", preset,
                "-acodec", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                output_path
            ]

            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Output:", result.stdout.decode("utf-8"))
            print("Errors:", result.stderr.decode("utf-8"))

            if os.path.exists(output_path):
                return output_path
            return None

    def convert_mov_to_mp4(self, input_path, output_path=None, crf=28, preset="slow"):
        ffmpeg_executable = r"F:\FFMPEG\bin\ffmpeg.exe"
        if output_path is None:
            base, _ = os.path.splitext(input_path)
            output_path = base + ".mp4"
        input_path = str(os.path.join(self.rel_path, input_path))
        output_path = str(os.path.join(self.rel_path, output_path))
        print(f"InPath : {input_path};\nOutPath: {output_path}")

        cmd = [
            ffmpeg_executable, "-i", input_path,
            "-f", "mp4",
            "-crf", str(crf),
            "-movflags", "+faststart",
            "-c:v", "copy",
            "-preset", preset,
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print("Output:", result.stdout.decode("utf-8"))
            print("Errors:", result.stderr.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print("FFmpeg error:", e.stderr.decode("utf-8"))
            return None

        if os.path.exists(output_path):
            return output_path
        return None

    def create_directory(self, day: int):
        script_dir = os.path.dirname(__file__)
        day_directory = os.path.join(script_dir, f"day_{day}")
        if not os.path.exists(day_directory):
            os.makedirs(day_directory)
            return True
        return False

    def ULTRA_MEGA_CONVERTOR(self, day, sch_db: ScheduleDatabase, preset="slow"):
        day_sch = sch_db.get_day(day)

        max_len = int(len(day_sch))
        print(f"int(len(day_sch)-1): {int(len(day_sch)-1)}")
        for f in range(0, max_len):
            if day_sch[f]['addition'] == "media":
                for path in day_sch[f]['path']:
                    print(f'".MOV" in path["path"]: {".MOV" in path["path"]}')
                    if path["format"] == "video" and ".MOV" in path["path"]:
                        path_ = re.sub(r"_p(\d+)_", re_functions.decrement, path["path"])
                        p = path_
                        inp = p
                        print(f"Path: {inp}")

                        st = self.convert_mov_to_mp4(input_path=inp, preset=preset)
        sch_db.update_video_extensions(day)

    def create_photo_path(self, day, post, part):
        script_dir = os.path.dirname(__file__)
        if part != -1:
            return [os.path.join(script_dir,f"day_{day}/d{day}_p{post}_{part}.jpg"), f"day_{day}\\d{day}_p{post}_{part}.jpg"]
        else:
            return [os.path.join(script_dir, f"day_{day}/d{day}_p{post}.jpg"),f"day_{day}\\d{day}_p{post}.jpg"]

    def create_video_path(self, day, post, part, ext):
        script_dir = os.path.dirname(__file__)
        if part != -1:
            return [os.path.join(script_dir,f"day_{day}/d{day}_p{post}_{part}.{ext}"),f"day_{day}\\d{day}_p{post}_{part}.{ext}"]
        else:
            return [os.path.join(script_dir, f"day_{day}/d{day}_p{post}.{ext}"), f"day_{day}\\{day}_p{post}.{ext}"]

if __name__ == "__main__":
    ah = Archive_Helper()
    sch_db = ScheduleDatabase()
    day = 1
    #ah.ULTRA_MEGA_CONVERTOR(day,sch_db)
    vid_path = "F:\Python_Project\SportBot\data\\archive\day_3\d3_p1_1.MOV"
    ah.video_compressor(vid_path)
    #sch_db.update_video_extensions(day)
