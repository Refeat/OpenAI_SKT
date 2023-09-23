# sudo apt-get install poppler-utils
# pip install pdf2image

from pdf2image import convert_from_path

def pdf_to_images(pdf_path, output_folder):
    # Convert PDF to list of images
    images = convert_from_path(pdf_path)

    # Save images to the desired output folder
    for i, image in enumerate(images):
        image.save(f"{output_folder}/page_{i + 1}.png", "PNG")

if __name__ == "__main__":
    pdf_path = "sample.pdf"  # Replace with your PDF file path
    output_folder = "./output_images"  # Replace with your desired output folder
    pdf_to_images(pdf_path, output_folder)
