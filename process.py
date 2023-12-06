from time import sleep
import os
import json
import subprocess

unprocessed_photo_dir = "discord/unprocessed-photo/"
unprocessed_dir = "discord/unprocessed/"
processed_dir = "discord/processed/"

while True:
    noface = False
    directory_contents = os.listdir(unprocessed_dir)
    if(len(directory_contents) > 0):
        for file in directory_contents:
            file_extension = file.split('.')[-1]

            if len(directory_contents) < 2:
                break
            
            if(file_extension != 'json'):
                parameters=[]
                with open(unprocessed_dir+file+'.json' ,'r') as parameter_file:
                    parameters = json.load(parameter_file)

                image = parameters['image']
                try:
                    completed_process = subprocess.run(f'python ./backend/run.py -s {unprocessed_dir+file} -t {unprocessed_photo_dir+image} -o {processed_dir+file}', shell=True, capture_output=True, text=True, check=True)
                    output_lines = completed_process.stdout.splitlines()
                    last_line = output_lines[-1]
                    if last_line == "[ROOP.FACE-SWAPPER] No face in source path detected.":
                        print("No face")
                        noface = True
                        with open(unprocessed_dir + file + '.json', 'r') as f:
                            data = json.load(f)
                        data["no_face"] = True
                        with open(unprocessed_dir + file + '.json', 'w') as f:
                            json.dump(data, f)
                        f.close()
                except Exception as e:
                    print(e)
                    os.remove(unprocessed_dir+file)
                    os.remove(unprocessed_photo_dir+image)
                    os.remove(unprocessed_dir+file+'.json')


                if(os.path.isfile(processed_dir+file) and not noface):
                    os.remove(unprocessed_dir+file)
                    os.remove(unprocessed_photo_dir+image)
                    os.rename(unprocessed_dir+file+'.json',processed_dir+file+'.json')
                elif(noface):
                    os.rename(unprocessed_dir+file,processed_dir+file)
                    os.rename(unprocessed_dir+file+'.json',processed_dir+file+'.json')
