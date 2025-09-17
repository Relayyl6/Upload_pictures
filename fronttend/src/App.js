import { useState, useRef } from "react";
import axios from "axios";

const fileTypes = [
    "image/apng",
    "image/bmp",
    "image/gif",
    "image/jpeg",
    "image/pjpeg",
    "image/png",
    "image/svg+xml",
    "image/tiff",
    "image/webp",
    "image/x-icon",
];

function validFileType(file) {
    return fileTypes.includes(file.type);
}

function returnFileSize(number) {
  if (number < 1e3) {
    return `${number} bytes`;
  } else if (number >= 1e3 && number < 1e6) {
    return `${(number / 1e3).toFixed(1)} KB`;
  }
  return `${(number / 1e6).toFixed(1)} MB`;
}


export const FileCard = ({name, size, img}) => {
    return (
        <div style={{
            backgroundColor: '#f9fafb',
            justifyContent: 'space-between',
            alignItems: 'center',
            display: 'flex',
            flexDirection: 'row',
            gap: '16px',
            padding: '16px',
            margin: '10px auto',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.07)',
            maxWidth: "500px",
            width: "100%"
        }}>
            <div>
                <p style={{ fontWeight: 'bold', fontSize: '1.1rem', marginBottom: '4px', color: 'black' }}>{name}</p>
                <p style={{ color: '#555', fontSize: '0.95rem' }}>{size}</p>
            </div>
            <img
                src={URL.createObjectURL(img)}
                alt={name}
                style={{
                    width: '100px',
                    height: '100px',
                    objectFit: 'cover',
                    borderRadius: '8px',
                    border: '1px solid #ddd',
                }}
            />
        </div>
    )
}

export default function App() {
    const inputRef = useRef(null);

    // const input = document.querySelector("input");
    // const preview = document.querySelector(".preview");

    // input.style.opacity = 0;

    const [ selectedFiles, setSelectedFiles ] = useState([]);

    const handleChange = (e) => {
        setSelectedFiles(Array.from(e.target.files));
    }

    const handleSubmit = async (e) => {
      e.preventDefault();
      // setSelectedFiles(Array.from(e.target.files));
      if (selectedFiles.length === 0) {
        alert("No files selected!");
        return;
      }

      const formData = new FormData();
      selectedFiles.forEach((file, index) => {
        formData.append("image", file);
      }); // must match backend

      for (let [key, value] of formData.entries()) {
        console.log(key, value);
      }

      try {
        const res = await axios.post("http://127.0.0.1:5000/upload", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }


        const text = await res.text();
        console.log("Server Response", text)
      } catch (e) {
        console.error("Upload Failed", e)
      }
    };

    return (
            <div style={{
                marginLeft: 'auto',
                marginRight: 'auto',
                display: 'flex', 
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                backgroundColor: "blue",
                height: "100%",
                paddingBottom: "20px",
                maxWidth: "700px",
                inset: "0",
                // position: "fixed",
                maxHeight: "800px",
                borderRadius: "10px",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)"
                }}>
            <h1>
                Upload Images for editing
            </h1>

            <form action="http://127.0.0.1:5000/upload" onSubmit={handleSubmit} method="post" encType="multipart/form-data" style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center"
            }}>
                <label
                    htmlFor="image"
                    style={{
                        display: "inline-block",
                        padding: "10px 20px",
                        background: "#007bff",
                        color: "#fff",
                        borderRadius: "4px",
                        cursor: "pointer",
                        marginBottom: "1rem",
                        fontWeight: "bold",
                        fontSize: "1rem",
                        textAlign: "center"
                    }}
                >
                    Select images to upload
                </label>
                <input
                    type="file"
                    id="image"
                    name="image"
                    multiple
                    ref={inputRef}
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={handleChange}
                />
                <div className="preview" style={{ display: "flex", flexDirection: "row" }}>
                {
                  selectedFiles.length === 0 ? (
                        <p>No files currently selected for upload</p>
                    ) : (
                        <ol >
                            {selectedFiles.map((file, index) => (
                                <li key={index} style={{ listStyle: 'none' }}>
                                    {validFileType(file) ? (
                                        <>
                                            {/* <p>{`File name ${file.name}, file size ${returnFileSize(file.size)}`}</p>
                                            <img
                                                src={URL.createObjectURL(file)}
                                                alt={file.name}
                                                style={{ maxWidth: "200px", maxHeight: "200px" }}
                                            /> */}
                                            <FileCard name={file.name} size={returnFileSize(file.size)} img={file}/>
                                        </>
                                    ) : (
                                        <>
                                            <p>{`File name ${file.name}, Not a valid file type. Update your selection`}</p>
                                        </>
                                    )}
                                </li>
                            ))}
                        </ol>
                  )
                }
                </div>
                <br />
                <button type="submit" name="submit">Upload and process</button>
            </form>
        </div>
    )
};

