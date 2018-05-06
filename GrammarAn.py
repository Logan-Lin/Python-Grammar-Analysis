import pandas
import os

coding_df = pandas.read_csv("data/coding.csv", delimiter=' ', index_col=0)
first_df = pandas.read_csv("data/first.csv", delimiter='`', index_col=[0, 2])
scan_index = 0


# Turn binary string such as (20, -) into coding integer.
def process_binary(bin_str):
    return int(bin_str[1:].split(",")[0])


def load_coding(file_name):
    """
    Load lexical analysis's output into coding array.

    Parameters
    ---------
    file_name: str
        Output file's directory
    """
    global coding_array
    coding_array = []
    with open(file_name, "r") as file:
        for row in file.readlines():
            if len(row) > 2:
                # If the row is not empty
                row_coding = list(map(process_binary, row.split(")")[:-1]))
                coding_array += row_coding


def get_current_description(column="secondary"):
    """
    Return current description based on current coding.

    Parameters
    ---------
    column: str
        Set the column to search for. Set to 'description' to search from original column.

    Raises
    -----
    ValueError if can't find description based on current coding

    Returns
    ------
    desc: str
        Description (identifier) current coding represented
    """
    coding = coding_array[scan_index]
    desc = coding_df.loc[coding][column]
    if not type(desc).__name__ == "str":
        raise ValueError("Identifier type not valid")
    return desc


def proceed(function):
    """
    The core of grammar analysis, proceed the formula based on function name

    Parameters
    ---------
    function: str
        The name of recursive sub-function to be proceed

    Raises
    ------
    KeyError if there is no matching formula or the current identifier don't match the founded formula
    """
    global scan_index
    try:
        # Try to fetch matching formula based on function name and current identifier
        formula = first_df.loc[function, get_current_description()]["formula"]
    except KeyError:
        # Can't find matching formula. Check if function can lead to empty formula
        try:
            formula = first_df.loc[function, 'e']
            scan_index -= 1
            return
        except KeyError:
            # Function can't lead to empty formula, the input series is invalid
            raise KeyError("No matching formula")
    for char in formula.split(' '):
        if char.isupper():
            # Character is an upper letter, meaning that it represents a function to be proceeded
            proceed(char)
        else:
            # Character is not an upper letter or it is not a letter, meaning that it is an identifier
            if not get_current_description() == char:
                raise KeyError("Identifier not matching")
        scan_index += 1
    scan_index -= 1


def scan_file(file_name):
    """
    Scan the input binary series from file and check if it is valid.

    Parameters
    ----------
    file_name: str
        The file storing binary series outputted from lexical analysis
    """
    load_coding(file_name)
    global scan_index
    scan_index = 0
    valid = False
    try:
        proceed("A")
        valid = True
    except (KeyError, ValueError) as e:
        print("Error at position {}, content: `{}`, type: {}".format(
            scan_index + 1, get_current_description("description"), e))
    except IndexError:
        valid = True
    if valid:
        print("Valid")


if __name__ == "__main__":
    for i in range(1, 5):
        file_dir = os.path.join("test", "in{}.txt".format(i))
        print("File {}: ".format(file_dir), end='')
        scan_file(file_dir)
