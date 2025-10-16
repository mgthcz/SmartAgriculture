import os

# 获取当前文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（向上两级到SmartAgriculture目录）
project_root = os.path.dirname(os.path.dirname(current_dir))

# 疾病检测模型配置
names = {0: "wilting", 1: "powdery_mildew", 2: "Spot_disease", 3: "viral_disease"}
names_china = {0: "萎蔫", 1: "白粉病", 2: "斑点病", 3: "病毒病"}  # 修正了1.0为1
model_path = os.path.join(project_root, "SmartAgriculture", "tool", "v8x_bad.pt")

# 成熟度检测模型配置
names_ripe = {0: 'ripe', 1: 'unripe'}
names_china_ripe = {0: '成熟', 1: '未成熟'}
model_path_ripe = os.path.join(project_root, "SmartAgriculture", "tool", "straw_ripe.pt")

# 草莓病害模型配置
names_bad = {0: "powdery", 1: "acalcerosis", 2: "fertilizer", 3: "greyleaf"}
names_china_bad = {0: "白粉病", 1: "缺钙症", 2: "肥害", 3: "灰叶病"}
model_path_bad = os.path.join(project_root, "SmartAgriculture", "tool", "straw_bad.pt")


# 验证模型文件是否存在
def check_model_files():
    """检查所有模型文件是否存在"""
    model_files = {
        'v8x_bad.pt': model_path,
        'straw_ripe.pt': model_path_ripe,
        'straw_bad.pt': model_path_bad
    }

    print("检查模型文件:")
    print("=" * 50)

    all_exist = True
    for name, path in model_files.items():
        exists = os.path.exists(path)
        status = "✅ 存在" if exists else "❌ 缺失"
        print(f"{status} {name}")
        print(f"   路径: {path}")

        if not exists:
            all_exist = False

    print("=" * 50)
    if all_exist:
        print("✅ 所有模型文件都存在")
    else:
        print("❌ 有模型文件缺失，请检查文件路径")

    return all_exist


# 可选：在导入时自动检查
if __name__ == "__main__":
    check_model_files()
else:
    # 在作为模块导入时也进行检查
    models_ready = check_model_files()