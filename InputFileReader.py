class InputFileReader:
    """
    A class to read input from a file and extract specific values.

    Attributes:
        file_path (str): The path to the input file.
    """

    def __init__(self, file_path):
        """
        Initializes the InputFileReader with the path to the input file.

        Args:
            file_path (str): The path to the input file.
        """
        self.file_path = file_path

    def read_lines(self):
        """
        Reads all lines from the input file.

        Returns:
            list: A list of lines read from the file, or None if an error occurs.
        """
        try:
            with open(self.file_path, 'r') as file:
                return file.readlines()

        except FileNotFoundError:
            print("Error: File not found")

        except Exception as e:
            print("Error occurred:", e)

    def get_value(self, field):
        """
        Extracts the value associated with a specific field from the input file.

        Args:
            field (str): The field whose value needs to be extracted.

        Returns:
            str: The value associated with the field, or None if the field is not found or an error occurs.
        """
        lines_list = self.read_lines()
        if lines_list is not None:
            for line in lines_list:
                if line.startswith(field):
                    val = line.split(field + ':')[1]  # Extracts message
                    if field == "message":
                        val = val.strip()  # Removes external spaces
                        val = val.strip('"')  # Removes external quotes
                    return val

        print("Unknown field or file is invalid")