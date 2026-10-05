from pathlib import Path

def find_note_files(dir,suffix):
    return [path for path in dir.rglob("*") if path.suffix in suffix]

def search_keyword(keyword,passage):
    res_paragraph = []
    for path in passage:
        content = path.read_text(encoding = "utf-8")
        for number,paragraph in enumerate(content.split("\n\n"),start= 1):
            if keyword.casefold() in paragraph.casefold():
                res_paragraph.append((path,number,paragraph))
    return res_paragraph

def load_paragraphs(notes_dir):
    results = []
    paths = find_note_files(notes_dir,[".txt",".md"])
    for path in paths:
        content = path.read_text(encoding = "utf-8")
        for number,paragraph in enumerate(content.split("\n\n"),start=1):
            text = paragraph.strip()
            if not text:
                continue
            results.append({"file": str(path.relative_to(notes_dir)), "paragraph": number, "text": text})
    return results

if __name__ == "__main__":
    notes_dir = Path(__file__).parent / "notes"
    keyword = ""
    while(1):
        keyword = input("请输入关键词:").strip()
        if keyword == '':
            print("你输入的内容为空")
        elif keyword == 'q':
            break
        else:
            passage = find_note_files(notes_dir,[".txt",".md"])
            cparagraph = search_keyword(keyword,passage)
            for path,number,paragraph in cparagraph:
                print(f"{path.relative_to(notes_dir)}｜段落:{number:02d}｜{paragraph.strip()[:100]}")
            count = len(cparagraph)
            if count == 0:
                print("未找到匹配的段落")
            else:
                print(f"找到了{count}段包含  {keyword}  的段落")
                
