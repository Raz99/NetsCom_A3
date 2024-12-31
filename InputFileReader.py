class InputFileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_lines(self):
        try:
            with open(self.file_path, 'r') as file:
                return file.readlines()

        except FileNotFoundError:
            print("Error: File not found")

        except Exception:
            print("Error occurred")

    def get_value(self, field):
        for line in self.read_lines():
            if line.startswith(field):
                val = line.split(field + ':')[1] # Extracts message
                no_spaces_line = val.strip() # Removes external spaces
                result = no_spaces_line.strip('"') # Removes external quotes
                if field == "maximum_msg_size" or field == "window_size" or field == "timeout":
                    return int(result)
                else:
                    return result
        print("Unknown field or file is invalid")

if __name__ == "__main__":
    file_reader = InputFileReader("input.txt")
    message = file_reader.get_value("message")
    print("Message:", message)