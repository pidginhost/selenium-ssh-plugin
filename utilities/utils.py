import softest
import logging
from openpyxl import load_workbook
import inspect


class Utils(softest.TestCase):
    def assert_list_item_text(self, dynamic_list, value):
        for item in dynamic_list:
            print("The text is: " + item.text)
            self.soft_assert(self.assertEquals, item.text, value)
            if item.text == value:
                print("assert pass")
            else:
                print("assert none")
        self.assert_all()

    @staticmethod
    def custom_logger(log_level=logging.DEBUG):
        # Set class/method name from where its called
        logger_name = inspect.stack()[1][3]
        # Create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        fh = logging.FileHandler('automation.log')
        # How I want my log to be formatted
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        # Add formatter to console or loghandler
        fh.setFormatter(formatter)
        # Add console handler to loger
        logger.addHandler(fh)
        return logger

    @staticmethod
    def read_data_from_excel_file(excel_file, sheet):
        datalist = []
        try:
            wb = load_workbook(filename=excel_file)
            sh = wb[sheet]
            row_ct = sh.max_row
            col_ct = sh.max_column

            for i in range(2, row_ct + 1):
                row = []
                for j in range(1, col_ct + 1):
                    cell_value = sh.cell(row=i, column=j).value
                    row.append(cell_value)
                datalist.append(row)
        except FileNotFoundError:
            print(f"Error: The file '{excel_file}' not found.")
        except Exception as e:
            print(f"An error occurred while reading the Excel file: {str(e)}")
        else:
            return datalist

        return None

    @staticmethod
    def get_current_function_name():
        return inspect.currentframe().f_back.f_code.co_name
