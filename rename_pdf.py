import os
import re
from pypdf import PdfReader

# ================= 配置区 =================
submissions_dir = 'test'   # 存放 PDF 的文件夹名称
quiz_name = 'Quiz1'        # Quiz 名称（如 Quiz2, Quiz3）
# =========================================

if not os.path.exists(submissions_dir):
    print(f"错误: 找不到文件夹 '{submissions_dir}'！")
    exit()

success_count = 0
files = [f for f in os.listdir(submissions_dir) if f.lower().endswith('.pdf')]

print(f"找到 {len(files)} 个 PDF 文件，开始解析内容...\n")

for filename in files:
    file_path = os.path.join(submissions_dir, filename)
    
    try:
        reader = PdfReader(file_path)
        first_page_text = reader.pages[0].extract_text()
        
        # 1. 优先尝试从 Gradescope 电子生成的表头提取（如 Student\nRuiyang Hu）
        match = re.search(r'Student\s*\n\s*([A-Za-z\s]+)', first_page_text)
        
        # 2. 如果没匹配到，尝试匹配 Print Your Name 后面的名字
        if not match:
            match = re.search(r'Print Your Name-?\s*\n\s*([A-Za-z\s]+)', first_page_text)

        if match:
            raw_name = match.group(1).strip().split('\n')[0].strip()
            name_parts = raw_name.split()
            
            if len(name_parts) >= 2:
                # 默认最后一部分为 Last Name，前面为 First Name
                first_name = " ".join(name_parts[:-1])
                last_name = name_parts[-1]
            else:
                first_name = ""
                last_name = raw_name
                
            # 清理名字中的非法字符
            first_name = re.sub(r'[^\w\s-]', '', first_name).strip()
            last_name = re.sub(r'[^\w\s-]', '', last_name).strip()

            # 拼装为 LastName_FirstName_QuizX.pdf 格式
            if first_name:
                new_name = f"{last_name}_{first_name}_{quiz_name}.pdf"
            else:
                new_name = f"{last_name}_{quiz_name}.pdf"
                
            new_path = os.path.join(submissions_dir, new_name)
            
            # 执行重命名
            os.rename(file_path, new_path)
            print(f"成功重命名: {filename} -> {new_name}")
            success_count += 1
        else:
            print(f"跳过: 文件 '{filename}' 第一页未能提取到学生姓名")
            
    except Exception as e:
        print(f"处理文件 '{filename}' 时出错: {e}")

print(f"\n全部处理完成！成功重命名了 {success_count} / {len(files)} 个文件。")
