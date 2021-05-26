import argparse
import os
import exif
import shutil
import time


# Globals
INPUT_DIRECTORY = 'input/'
OUTPUT_DIRECTORY = 'output/'
CLEAN_ENABLED = False


def main():
    start = time.process_time()
    apply_args()
    for root, directories, files in os.walk(INPUT_DIRECTORY):
        # pixel image folers
        if os.path.basename(root).startswith(tuple(['IMG_', 'PXL_'])):
            process_image_folder(root, files)
            directories[:] = []
            continue

        # ignore trashed directories
        for directory in directories:
            if directory.startswith(tuple(['.', 'thumbnails'])):
                directories[:].remove(directory)
                print(f'IGNORING {os.path.join(root, directory)}')

        for file in files:
            # ignore trashed files
            if file.startswith('.'):
                continue
            process_file(root, file)
    if CLEAN_ENABLED:
        clean_input_directory()
    end = time.process_time()
    elapsed_time = end - start
    print(f'Elapsed time: {elapsed_time}s')


def process_image_folder(root, files):
    folder_name = os.path.basename(root)
    next_filename = f'{folder_name}.jpg'
    if len(files) == 1:
        try:
            curr_filepath = os.path.join(root, files[0])
            next_filepath = os.path.join(root, next_filename)
            os.rename(curr_filepath, next_filepath)
        except:
            print(f'ERROR: UNABLE TO RENAME {curr_filepath}')
        process_file(root, next_filename)
        return

    for file in files:
        if file.endswith('_COVER.jpg'):
            try:
                curr_filepath = os.path.join(root, file)
                next_filepath = os.path.join(root, next_filename)
                os.rename(curr_filepath, next_filepath)
            except: 
                print(f'ERROR: UNABLE TO RENAME {curr_filepath}')
            process_file(root, next_filename)
            return


def process_file(directory, filename):
    origin = os.path.join(directory, filename)
    if not filename.endswith(tuple(['.jpg', '.mp4'])):
        print(f'ERROR: INCORRECT FORMAT {os.path.join(directory, filename)}')
        return

    if filename.startswith(tuple(['VID_', 'IMG_', 'PXL_'])):
        year = filename[4:8]
        month = filename[8:10]
    else:
        try:
            with open(os.path.join(directory, filename), 'rb') as image_file:
                my_image = exif.Image(image_file)
            date_taken = my_image.datetime_original
            year = date_taken[0:4]
            month = date_taken[5:7]
        except:
            print(f'ERROR: CAN NOT SCRAPE DATA FOR {os.path.join(directory, filename)}')
            return
    destination = os.path.join(OUTPUT_DIRECTORY, year, month)
    move_file(origin, destination)


def move_file(origin, destination):
    try:
        os.makedirs(destination, exist_ok=True)
        shutil.move(origin, destination)
    except:
        print(f'ERROR: CAN NOT MOVE FILE {origin} to {destination}')


def clean_input_directory():
    for root, dirs, files in os.walk(INPUT_DIRECTORY, topdown = False):
        if not dirs and not files:
            os.rmdir(root)


def apply_args():
    global INPUT_DIRECTORY, OUTPUT_DIRECTORY, CLEAN_ENABLED

    parser = argparse.ArgumentParser(description="Camera Importer")
    parser.add_argument('-i',
                        '--input',
                        help="Specify an input directory",
                        default='input/')

    parser.add_argument('-o',
                        '--output',
                        help="Specify an output directory",
                        default='output/')
                        
    parser.add_argument('--clean',
                        help="Remove all empty subdirectories from input folder")

    args = parser.parse_args()
    if args.clean:
        CLEAN_ENABLED = True
    if not os.path.isdir(args.input):
        print("ERROR: INVALID INPUT DIRECTORY")
        quit(1)
    INPUT_DIRECTORY = args.input
    OUTPUT_DIRECTORY = args.output


if __name__ == "__main__":
    main()
