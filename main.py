import input_handler
import solution  
import json

def main():
    # folder_path = input("Nhập đường dẫn thư mục chứa file JSON: ")
    # if not os.path.isdir(folder_path):
    #     print(f"Error: Folder {folder_path} does not exist")
    #     sys.exit(1)
    #
    # stock_code = input("Nhập mã chứng khoán (tên file JSON): ")
    # json_path = os.path.join(folder_path, f"{stock_code}.json")
    #
    # if not os.path.exists(json_path):
    #     print(f"Error: File {json_path} does not exist")
    #     sys.exit(1)
    #
    # if not json_path.endswith('.json'):
    #     print("Error: Input file must be a JSON file")
    #     sys.exit(1) 

    json_path = "./TCH.json"
    
    print(f"processing {json_path}...") 

    # đọc input từ file json thành list trong python 
    all_rows:list = input_handler.json_to_py(json_path)           


    # Xử lý lỗi bất đồng bộ của data 
    fixed_rows, logs = solution.fix_sync(all_rows)  

    # in logs để debug
    print("Log chỉnh trật tự: ",json.dumps(logs, indent=4, ensure_ascii=False))
    # Xuất ra excel 
    input_handler.py_to_excel(fixed_rows, "./TCH_fixed.xlsx")


    print("✅ Processing complete!") 

def test_gather_chunks():  
    all_rows:list = input_handler.json_to_py("./TCH.json")           
    # Test gather_chunks function
    chunks = solution.gather_chunks(all_rows) 

    new_list = solution.edit_rows_based_on_chunks(all_rows, chunks)  
    input_handler.py_to_excel(new_list, "./TCH_chunking.xlsx")

if __name__ == "__main__": 
    # test_gather_chunks()
    main()
