class InputFileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_lines(self):
        try:
            with open(self.file_path, 'r') as file:
                return file.readlines()

        except FileNotFoundError:
            print("Error: File not found")

        except Exception as e:
            print("Error occurred:", e)

    def get_value(self, field):
        lines_list = self.read_lines()
        if lines_list is not None:
            for line in lines_list:
                if line.startswith(field):
                    val = line.split(field + ':')[1] # Extracts message
                    if field == "message":
                        val = val.strip() # Removes external spaces
                        val = val.strip('"') # Removes external quotes
                    return val

        print("Unknown field or file is invalid")