import pandas as pd
import os
import xml.etree.ElementTree as ET

# Nombre de la columna que contiene los enlaces de las imágenes en el archivo CSV
IMAGE_COLUMN_CSV = 'image_link'
# Nombre de la columna que contiene las referencias en el archivo CSV
REFERENCE_COLUMN_CSV = 'id'

# Nombre del tag que contiene los enlaces de las imágenes en el archivo XML
IMAGE_TAG_XML = 'image'
# Nombre del tag que contiene las referencias en el archivo XML
REFERENCE_TAG_XML = 'reference'

csv_file_name = 'feed.csv'
xml_file_name = 'feed.xml'
csv_file_path = os.path.join(os.path.dirname(__file__), csv_file_name)
xml_file_path = os.path.join(os.path.dirname(__file__), xml_file_name)

def process_csv(file_path, image_column, reference_column):
    df = pd.read_csv(file_path)
    
    missing_columns = []
    if image_column not in df.columns:
        missing_columns.append(image_column)
    if reference_column not in df.columns:
        missing_columns.append(reference_column)
    
    if missing_columns:
        raise ValueError(f"No se encontraron las siguientes columnas en el archivo CSV: {', '.join(missing_columns)}. "
                         f"Por favor, actualiza el script para usar los nombres de columna correctos.")
    
    images = df[image_column].tolist()
    references = df[reference_column].tolist()
    
    return list(zip(references, images))

def process_xml(file_path, image_tag, reference_tag):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    if not any(item.find(image_tag) is not None for item in root.findall('item')):
        raise ValueError(f"No se encontró el tag '{image_tag}' en el archivo XML. "
                         f"Por favor, actualiza el script para usar el nombre de tag correcto.")
    
    if not any(item.find(reference_tag) is not None for item in root.findall('item')):
        raise ValueError(f"No se encontró el tag '{reference_tag}' en el archivo XML. "
                         f"Por favor, actualiza el script para usar el nombre de tag correcto.")
    
    images_references = []
    for item in root.findall('item'):
        image = item.find(image_tag)
        reference = item.find(reference_tag)
        if image is not None and image.text and reference is not None and reference.text:
            images_references.append((reference.text, image.text))
    
    return images_references

def generate_html(images_references, output_path):
    items_string = ', '.join([f"{{reference: '{ref}', url: '{img}', title: 'Image {i+1}'}}" for i, (ref, img) in enumerate(images_references)])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Gallery</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .gallery {{ display: flex; flex-direction: column; }}
            .gallery img {{ max-width: 100%; margin: 5px 0; }}
            .item {{ margin-bottom: 20px; }}
            .pagination {{ margin: 20px 0; text-align: center; }}
            .pagination button {{ padding: 10px 15px; margin: 0 5px; }}
            hr{{height: 12px; background: black; width: 100%;}}
        </style>
    </head>
    <body>
    
    <div class="gallery" id="gallery"></div>
    <div class="pagination" id="pagination"></div>
    
    <script>
        const images = [{items_string}];
        const itemsPerPage = 5;
        let currentPage = 1;
    
        function renderGallery(page) {{
            const startIndex = (page - 1) * itemsPerPage;
            const endIndex = page * itemsPerPage;
            const gallery = document.getElementById('gallery');
            gallery.innerHTML = '';
            images.slice(startIndex, endIndex).forEach((item, index) => {{
                const div = document.createElement('div');
                div.className = 'item';
                const reference = document.createElement('p');
                reference.textContent = 'Reference: ' + item.reference;
                const img = document.createElement('img');
                img.src = item.url;
                img.alt = item.title;
                div.appendChild(reference);
                div.appendChild(img);
                gallery.appendChild(div);
                
                // Añadir separación solo si no es el último elemento
                if (index < endIndex - startIndex - 1) {{
                    const hr = document.createElement('hr');
                    gallery.appendChild(hr);
                }}
            }});
        }}
    
        function renderPagination() {{
            const pageCount = Math.ceil(images.length / itemsPerPage);
            const pagination = document.getElementById('pagination');
            pagination.innerHTML = '';
            for (let i = 1; i <= pageCount; i++) {{
                const button = document.createElement('button');
                button.innerText = i;
                button.onclick = () => {{
                    currentPage = i;
                    renderGallery(i);
                }};
                pagination.appendChild(button);
            }}
        }}
    
        document.addEventListener('DOMContentLoaded', () => {{
            renderGallery(currentPage);
            renderPagination();
        }});
    </script>
    
    </body>
    </html>
    """
    
    with open(output_path, 'w') as file:
        file.write(html_content)

    print(f"Archivo HTML generado: {output_path}")

def main():
    choice = input("¿Qué tipo de archivo deseas procesar (csv/xml)? ").strip().lower()
    if choice == 'csv':
        if not os.path.isfile(csv_file_path):
            raise FileNotFoundError(f"El archivo '{csv_file_path}' no se encontró.")
        images_references = process_csv(csv_file_path, IMAGE_COLUMN_CSV, REFERENCE_COLUMN_CSV)
    elif choice == 'xml':
        if not os.path.isfile(xml_file_path):
            raise FileNotFoundError(f"El archivo '{xml_file_path}' no se encontró.")
        images_references = process_xml(xml_file_path, IMAGE_TAG_XML, REFERENCE_TAG_XML)
    else:
        print("Opción no válida. Por favor, elige 'csv' o 'xml'.")
        return
    
    html_file_path = os.path.join(os.path.dirname(__file__), 'image_gallery.html')
    generate_html(images_references, html_file_path)

if __name__ == "__main__":
    main()
