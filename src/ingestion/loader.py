import os
EXTENSION_LANGUAGE_MAP={
    '.py': 'python',
    '.js': 'javascript',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.rb': 'ruby',
    '.go': 'go',
    '.rs': 'rust'
}
def is_binary_file(file_path:str)->bool:
    """check if the file is a binary file"""
    try:
        with open(file_path,'rb') as f:
            chunk=f.read(1024)
            return b"\0" in chunk
    except:
        return True
def detect_lang(file_path:str)->str:
    """DETECT THE LANGUAGE OF THE FILE"""
    _,ext=os.path.splitext(file_path)
    return EXTENSION_LANGUAGE_MAP.get(ext.lower(),'unknown')
def read_file(file_path:str)->str:

    """ read the contents of the file and store it in a dict
    {
    path:str
    language:str
    encoding:str
    content:str
    }
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    if is_binary_file(file_path):
        raise ValueError(f"File {file_path} is a binary file")
    try:
        with open(file_path,'r',encoding='utf-8') as f:
            content=f.read()
            encoding='utf-8'
    except UnicodeDecodeError:
        with open(file_path ,'r',encoding='latin-1') as f:
            content=f.read()
            encoding='latin-1'
    return {
        "path":file_path,
        "language":detect_lang(file_path),
        "encoding":encoding,
        "content":content
    }
def load_files_from_directory(file_paths:list)->list:
    """load files from a list of file paths"""
    results=[]
    for path in file_paths:
        try:
            results.append(read_file(path))
        except Exception as e:

            results.append({
    "path": path,
    "error": str(e),
    "language": "unknown",
    "content": ""
})
    return results
if __name__=="__main__":
    test_files=["sample.py","sample.js","sample.java","sample.cpp"]
    results=load_files_from_directory(test_files)
    for file in results:
        print(file["path"])
        print(file.get("content",""))
        print(file.get("error"))