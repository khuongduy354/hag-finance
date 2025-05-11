import itertools 
import datetime
import input_handler


def is_giao_dich(row)->bool:   
    must_not_change_field = ["Khối lượng", "Giá", "Loại"]   

    for f in must_not_change_field:   
        if row[f] != "":
            return False  
    return True 

def is_lenh(row)->bool: 
    return not is_giao_dich(row) and row["Loại"] != ""

def is_in_time_interval(t1: dict, t2: dict, interval: int = 1) -> bool:  
    t1 = t1["Thời gian"]
    t2 = t2["Thời gian"]
    """
    Kiểm tra xem t1 và t2 có cách nhau interval giấy không 
    """
    time_format = "%H:%M:%S"
    t1_obj = datetime.datetime.strptime(t1, time_format)
    t2_obj = datetime.datetime.strptime(t2, time_format)
    
    # Tính khoảng cách giữa hai thời gian
    delta = abs((t2_obj - t1_obj).total_seconds())
    
    return delta <= interval

def get_list(l: list, idx:int):  
    if idx < 0:   
        return None  

    if idx >= len(l): 
        return None 

    return l[idx]

def lambda_in_time(t1:dict, interval:int = 1):  
    return lambda x: is_in_time_interval(t1, x, interval) or is_in_time_interval(x, t1, interval)

def get_row_at_idx(l: list, idx: int, c: list[callable]):  
    item = get_list(l,idx)  
    if item is None: 
        return None 
    else:
        for func in c:
            if not func(item): 
                return None
        return item

def gather_chunks(all_rows: list) -> list: 
    i = 0 
    chunk = []
    chunks:list[list] = [] 
    while i < len(all_rows):  
        row = all_rows[i] 
        if is_lenh(row): 
            next_gd = get_row_at_idx(all_rows, i + 1, [lambda_in_time(row), is_giao_dich]) 
            if next_gd:  
                chunk.append({"row": row, "idx": i})     

                chunk.append({"row": next_gd, "idx": i + 1}) 
                i += 1

        if len(chunk) > 0:
            chunks.append(chunk)
        chunk = []
        i += 1

    for c in chunks:  
        for row in c:  
            row["row"]["Đánh dấu cụm"] = True

    # chunks = [ 
    #     [{row: r1, idx: i1}, {row: r2, idx: i2}] 
    #     [{row:r3, idx: i3}, {row: r4, idx: i4}]
    # ]
         
    return chunks  


def edit_rows_based_on_chunks(all_rows: list, chunks: list) -> list:   
    new_list = all_rows.copy()  
    for chunk in chunks:  
        for row in chunk:    
            # for every row in chunk 
            # find row in original list 
            # edit it 
            for i in range(len(all_rows)):  
                if row.get("row") is None or row.get("row").get("Thời gian") is None: 
                    raise ValueError("Chunk format lỗi: ", row) 

                if all_rows[i]["Thời gian"] == row["row"]["Thời gian"]:   
                    # print("rewriting row: ", all_rows[i]["Thời gian"]) 
                    # print("row", row["row"])
                    new_list[i] = row["row"] 
                    break

    return new_list 


def fix_sync(all_rows: list) -> list:     
    new_rows = all_rows.copy()

    # Gom cụm 
    chunks = gather_chunks(all_rows)
    logs = [] 
    print("Tổng số cụm: ", len(chunks))  


    # Xử lý từng cụm
    new_chunks = []
    for i,_chunk in enumerate(chunks):     
        if len(_chunk) <= 1:  
            raise ValueError("Cụm không hợp lệ: ", _chunk)

        # _chunk = sorted(_chunk, key=lambda x: x["row"]["Thời gian"]) 
        # chunk = [x["row"] for x in _chunk]  
        # start_row = _chunk[0]["idx"]

        # Nhớ thứ tự 
        # giao_dich_order = list(filter(is_giao_dich,chunk))
        # lenh_order = list(filter(lambda x: not is_giao_dich(x), chunk))
        
        # Hoán vị    
        # perms = [list (p) for p in itertools.permutations(chunk)]

        # # Lọc các hoán vị không đúng thứ tự 
        # valid_perms = []
        # for p in perms:      
        #     giao_dich_part = list(filter(is_giao_dich, p))
        #     lenh_part = list(filter(lambda x: not is_giao_dich(x), p))

        #     if giao_dich_part == giao_dich_order and lenh_part == lenh_order:  
        #         valid_perms.append(p) 


        # Tính tổng    
        valid_perms = []
        valid_perms.append(_chunk)   
        valid_perms.append(_chunk[::-1]) 

        min_sum = float("inf") 
        best_perm_idx = -1   
        for i,p in enumerate(valid_perms):     
            sum = 0 

            # Lấy độ lệch từng hoán vị
            for j,row in enumerate(p):   
                row = row["row"]
                if j == len(p) - 1:
                    # Nếu là dòng cuối thì không cần tính
                    break

                delta = 0 

                # Dòng lệnh: Tăng/giảm = Chờ_mới - Chờ_cũ + KL_lệnh. 
                next_row = p[j+1]["row"]     
                if not is_giao_dich(row):    
                    delta = next_row["Chờ mua 1"] - row["Chờ mua 1"] + input_handler.to_float(row["Khối lượng"])  
                else: 
                    # Dòng giao dịch: Tăng/giảm = Chờ_mới - Chờ_cũ (không cộng KL_lệnh).
                    delta = next_row["Chờ mua 1"] - row["Chờ mua 1"] 
                 
                sum += abs(delta) 

            # Chọn hoán vị tổng nhỏ nhất
            if sum < min_sum:  
                min_sum = sum
                best_perm_idx = i
        

        if best_perm_idx == -1:  
            raise ValueError("Không tìm thấy hoán vị hợp lệ") 
        
        best_perm = valid_perms[best_perm_idx]
        changed = best_perm_idx != 0
        sorted_time = sorted([x["row"]["Thời gian"] for x in best_perm], key=lambda x: datetime.datetime.strptime(x, "%H:%M:%S"), reverse=True)

        for i in range(len(best_perm)): 
            best_perm[i]["row"]["Thời gian"] = sorted_time[i] 

        if not changed:  
            for i in range(len(best_perm)): 
                best_perm[i]["row"]["Đánh dấu cụm"] = False 
        new_chunks.append(best_perm) 


        logs.append({  
            "Timestamp ảnh hưởng ": [x["row"]["Thời gian"] for x in _chunk],
            "Có thay đổi: ": changed,  
            "Message: ": "Đã hoán vị cụm này" if changed else "Không có thay đổi",
            # "Thứ tự gốc: ": [x["Thời gian"] for x in _chunk],
            # "Thứ tự mới: ": [x["Thời gian"] for x in best_perm],
        })   

    new_rows = edit_rows_based_on_chunks(new_rows, new_chunks)
    
    return new_rows, logs
