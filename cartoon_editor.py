from pathlib import Path
import re
from PIL import Image
import cv2
import numpy as np

class CartoonImageEditor:
    def __init__(self, min_cut_size = None, max_cut_size=None):
        self.min_cut_size = min_cut_size
        self.max_cut_size = max_cut_size

    def extract_order(self, text):
        return [int(num) for num in re.findall(r'\d+', text)][-1]

    def load_images(self, dir):
        files = list(Path(dir).glob("*"))
        files = sorted(files, key = lambda x : self.extract_order(str(x)))
        images = [Image.open(file) for file in files]
        return images
        
    def image_stitch(self, images, split_line = False, split_line_thickness=3):
        images = [np.array(img) for img in images]
        if split_line:
            black_line = images[0][:split_line_thickness, :, :]*0
            images = [[image, black_line.copy()]for image in images]
            images = sum(images, [])[:-1]
        return Image.fromarray(cv2.vconcat(images))

    def extract_split_ranges(self, image:Image):
        image = np.array(image)
        color_line = np.average(np.average(image, axis=1), axis=1)
        i = 0
        l = len(color_line)
        
        ranges = [] # (from, to) list 이때 to는 바로 앞에 인덱스까지만 포함
        while i < l:
            # if l-i <= self.min_cut_size:
            #     ranges.append([i, l])
            #     break
            if color_line[i] == 255:
                i+=1
                continue
            else:
                j = i+1
                while (j < l) and ((color_line[j] != 255) or (self.min_cut_size and j-i < self.min_cut_size)):
                    if self.max_cut_size and (j-i < self.max_cut_size):
                        break
                    j += 1
                ranges.append([i, j+1])
                i = j+1
        return ranges
        
    def image_split(self, image, ranges):
        image = np.array(image)
        splited_images = []
        for a, b in ranges:
            splited_images.append(Image.fromarray(image[a:b, :, :]))
        return splited_images
    
    def save_images(self, images, title):
        title = Path(title)
        title.mkdir(parents=True, exist_ok=True)
        for i, image in enumerate(images):
            image.save(title/f"cut_{i+1}.png")