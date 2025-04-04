from PIL import Image

# 載入 PNG 圖片
input_path = r"C:\Users\lolJames\OneDrive\桌面\UI\icons\yoga-logo.png"  # 替換成你的圖片路徑
output_path = r"C:\Users\lolJames\OneDrive\桌面\UI\icons\yoga-logo_resized.png"

# 開啟圖片
img = Image.open(input_path)

# 縮放圖片為 20x20
resized_img = img.resize((30, 30))

# 儲存縮放後的圖片
resized_img.save(output_path)

print(f"圖片已成功縮放並儲存至 {output_path}")