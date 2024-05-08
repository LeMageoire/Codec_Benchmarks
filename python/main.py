
import argparse

def main():
    """
    test
    """
    parser = argparse.ArgumentParser(description="test")
    parser.add_argument("input", help="input file")
    parser.add_argument("output", help="output file")
    args = parser.parse_args()
    print(args.input)
    print(args.output)

    # call the encoder function here (encoder.py from forked repo that is a .gitmodules)
    




if __name__ == "__main__":
    main()