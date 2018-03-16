import tarfile
import argparse
import os


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The name of the file to be processed', required=True)
    args = argparser.parse_args()

    file = args.f
    filename = file.split("/")[-1].split(".")[0]
    archive_name = filename + '.tar.gz'
    print()
    print("------> Compressing file:", file, "<------")

    tar = tarfile.open(archive_name, "w:gz")
    tar.add(file, os.path.basename(file))
    tar.close()

    print()
    print("------> Compressed as:", archive_name, "<------")


if __name__ == "__main__":
    main()