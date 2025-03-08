import subprocess
from collections import defaultdict

def get_git_log():
    """获取git日志输出"""
    cmd = "git log --pretty=format:\"---%n%an\" --name-only"
    log_output = subprocess.check_output(
        cmd,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='latin-1'
    )
    return log_output

# def parse_log_output(log_output):
#     """解析git日志输出，统计每个作者在每个文件夹（包括二级目录）下的提交次数"""
#     author_folder_stats = defaultdict(lambda: defaultdict(int))
#     current_author = None

#     for line in log_output.splitlines():
#         line = line.strip()
#         if line.startswith('---'):
#             # 新的提交开始
#             current_author = None
#         elif line:
#             if current_author is None:
#                 current_author = line
#             else:
#                 # 提取文件路径，并统计其所在的文件夹（包括二级目录）
#                 file_path = line
#                 if '/' in file_path:
#                     # 分割路径，获取一级和二级目录
#                     parts = file_path.split('/')
#                     if len(parts) >= 2:
#                         folder = '/'.join(parts[:2])
#                     else:
#                         folder = parts[0]
#                 else:
#                     folder = 'root'
#                 author_folder_stats[current_author][folder] += 1
#     return author_folder_stats
def parse_log_output(log_output):
    """解析git日志输出，统计每个作者在每个目录层级下的提交次数"""
    author_folder_stats = defaultdict(lambda: defaultdict(int))
    current_author = None

    for line in log_output.splitlines():
        line = line.strip()
        if line.startswith('---'):
            # 新的提交开始
            current_author = None
        elif line:
            if current_author is None:
                current_author = line
            else:
                # 提取文件路径，并统计其所在的目录层级
                file_path = line
                if '/' in file_path:
                    # 分割路径，获取一级、二级、三级目录
                    parts = file_path.split('/')
                    for i in range(1, min(len(parts) + 1, 4)):  # 最多统计到三级目录
                        folder = '/'.join(parts[:i])
                        author_folder_stats[current_author][folder] += 1
                else:
                    folder = 'root'
                    author_folder_stats[current_author][folder] += 1
    return author_folder_stats

def filter_stats(author_folder_stats):
    """过滤掉提交次数为1的记录"""
    filtered_stats = defaultdict(dict)
    for author, folders in author_folder_stats.items():
        for folder, count in folders.items():
            if count > 1:
                filtered_stats[author][folder] = count
    return filtered_stats

def main():
    log_output = get_git_log()
    author_folder_stats = parse_log_output(log_output)
    filtered_stats = filter_stats(author_folder_stats)

    # 打印统计结果
    for author, folders in filtered_stats.items():
        print(f"Author: {author}")
        # 按目录层级排序：一级目录 -> 二级目录 -> 三级目录
        sorted_folders = sorted(folders.items(), key=lambda x: (x[0].count('/'), x[0]))
        for folder, count in sorted_folders:
            print(f"  Folder: {folder}, Commits: {count}")
        print()

    # 建议CODEOWNERS配置
    print("Suggested CODEOWNERS entries:")
    for author, folders in filtered_stats.items():
        if not folders:
            continue
        # 找出提交次数最多的目录
        main_folder = max(folders, key=lambda x: (folders[x], len(x.split('/'))))
        print(f"{main_folder}/  @{author}")

if __name__ == "__main__":
    main()
