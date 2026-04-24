from paddleocr import PaddleOCR
import pprint
import cv2
import numpy as np
import os

# ===========================
# 1️⃣ 初始化 PaddleOCR
# ===========================
LIMIT_SIDE_LEN = 1200  # 最大边长，可根据电脑性能调整

# ocr = PaddleOCR(
#     lang="ch",
#     use_textline_orientation=False,  # 替代旧参数 use_angle_cls
#     text_det_limit_side_len=LIMIT_SIDE_LEN  # 替代旧参数 det_limit_side_len
# )


# --- 使用相对路径加载模型 ---
# 它们相对于 01_Test_paddle.py 文件
BASE_MODEL_DIR = "ORC_models"  # 基础模型文件夹名称

# 使用 os.path.join 确保跨系统兼容性
DET_MODEL_PATH = os.path.join(BASE_MODEL_DIR, "ch_PP-OCRv3_det_infer")
REC_MODEL_PATH = os.path.join(BASE_MODEL_DIR, "ch_PP-OCRv3_rec_infer")
# 请确保 CLS 模型文件夹内有 inference.yml
CLS_MODEL_PATH = os.path.join(BASE_MODEL_DIR, "ch_ppocr_mobile_v2.0_cls_infer")

ocr = None
try:
    # 使用新的参数名以避免未来的 DeprecationWarning
    ocr = PaddleOCR(
        text_detection_model_dir=DET_MODEL_PATH,      # 新的检测模型参数名
        text_recognition_model_dir=REC_MODEL_PATH,    # 新的识别模型参数名
        textline_orientation_model_dir=CLS_MODEL_PATH,# 新的分类模型参数名

        # 其他参数
        use_textline_orientation=True,  # 启用方向分类
        text_det_limit_side_len=LIMIT_SIDE_LEN,
        # 移除 show_log=False
    )
    print("✅ PaddleOCR 离线模式初始化成功，已加载本地模型。")

except Exception as e:
    print(f"❌ 严重错误：PaddleOCR 初始化失败。错误信息: {e}")
    print(f"   请检查以下路径的模型文件是否完整（包括 inference.yml）：")
    print(f"   检测模型目录: {os.path.abspath(DET_MODEL_PATH)}")
    print(f"   识别模型目录: {os.path.abspath(REC_MODEL_PATH)}")
    print(f"   分类模型目录: {os.path.abspath(CLS_MODEL_PATH)}")
    # 如果初始化失败，则终止程序
    exit(1)


# ... 后续的识别和车牌筛选代码 ...




# 图片路径
img_path = r"C:\Users\Administrator\Pictures\test.jpg"

# ===========================
# 2️⃣ OCR 识别
# ===========================
raw_results = ocr.predict(img_path)

# 打印原始结果（方便调试）
print("\n--- 原始 OCR 输出 ---")
pprint.pprint(raw_results)

# ===========================
# 3️⃣ 解析 OCR 结果
# ===========================
def parse_ocr_results(results):
    """解析 PaddleOCR 输出为统一格式"""
    clean_data = []

    if not results or not isinstance(results, list):
        print("❌ OCR 结果为空或格式错误")
        return clean_data

    ocr_result = results[0]

    polys = ocr_result.get("rec_polys") or ocr_result.get("dt_polys") or []
    texts = ocr_result.get("rec_texts") or []
    scores = ocr_result.get("rec_scores") or []

    for i in range(min(len(polys), len(texts))):
        polygon = polys[i]
        text = texts[i]
        score = float(scores[i]) if i < len(scores) else None

        if isinstance(polygon, np.ndarray):
            polygon = polygon.tolist()

        clean_data.append({
            "text": text,
            "score": score,
            "polygon": polygon
        })

    return clean_data

cleaned_results = parse_ocr_results(raw_results)


''''
# ===========================
# 4️⃣ 绘制 OCR 边界框（原图尺寸）
# ===========================
def draw_ocr_boxes_original_size(img_path, raw_results, clean_data, output_path="test_aligned_boxes_original.jpg"):
    """在原图尺寸上绘制 OCR 框，保证位置与识别结果完全对应"""
    # --- 读取原图 ---
    original_img = cv2.imread(img_path)
    if original_img is None:
        print(f"❌ 无法读取图片: {img_path}")
        return

    h_orig, w_orig = original_img.shape[:2]

    # --- 获取 PaddleOCR 预处理图像（用于坐标映射） ---
    preprocessed_img = None
    if isinstance(raw_results, list) and len(raw_results) > 0:
        doc_pre = raw_results[0].get("doc_preprocessor_res", {})
        if doc_pre and isinstance(doc_pre.get("output_img"), np.ndarray):
            preprocessed_img = doc_pre["output_img"]

    if preprocessed_img is not None:
        h_pre, w_pre = preprocessed_img.shape[:2]
        scale_x = w_orig / w_pre
        scale_y = h_orig / h_pre
        print(f"✅ 找到 PaddleOCR 预处理图，缩放比例: scale_x={scale_x:.4f}, scale_y={scale_y:.4f}")
    else:
        # 如果没有预处理图，就使用原图，比例为 1
        preprocessed_img = original_img.copy()
        scale_x = scale_y = 1.0
        print("⚠️ 未找到预处理图像，直接在原图上绘制，可能会有轻微偏差")

    # --- 绘制框 ---
    img = original_img.copy()
    LINE_THICKNESS = max(2, int(min(w_orig, h_orig)/500))  # 根据图像尺寸自动调整线宽
    COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

    print("\n--- 在原图上绘制边界框 ---")
    for i, item in enumerate(clean_data):
        polygon = item.get("polygon")
        if not polygon:
            continue

        # 缩放坐标到原图尺寸
        polygon_scaled = [[int(x * scale_x), int(y * scale_y)] for x, y in polygon]

        pts = np.array(polygon_scaled, np.int32).reshape((-1, 1, 2))
        color = COLORS[i % len(COLORS)]
        cv2.polylines(img, [pts], isClosed=True, color=color, thickness=LINE_THICKNESS)

        print(f"绘制第 {i + 1} 个框，颜色：{color}，文本：{item.get('text')}")

    cv2.imwrite(output_path, img)
    print(f"✅ 已保存标注结果到: {output_path}")

# ===========================
# 5️⃣ 执行绘制函数
# ===========================
output_dir = os.path.dirname(img_path)
output_filename = "test_aligned_boxes_FINAL_original.jpg"
absolute_output_path = os.path.join(output_dir, output_filename)

draw_ocr_boxes_original_size(img_path, raw_results, cleaned_results, absolute_output_path)
'''
# ===========================
# 6️⃣ 打印整理后的 OCR 结果
# ===========================
print("\n--- 提取和整理后的 OCR 识别结果 ---")
pprint.pprint(cleaned_results)
