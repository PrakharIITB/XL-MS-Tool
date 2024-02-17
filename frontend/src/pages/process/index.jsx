import { useEffect, useState } from "react";
import axios from "axios";
import "./style.css";
import Button from "@mui/material/Button";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import VisuallyHiddenInput from "../components/hiddenInput";
import Processing from "./processing";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
// import ParseCSV from "../components/csvParser";

const Process = () => {
  const [file, setFile] = useState(null);
  const [db, setDb] = useState(null);
  const [zip, setZip] = useState(null);
  const [choice, setChoice] = useState("");
  const [mode, setMode] = useState("");
  const [dbName, setDbName] = useState("");
  const [zipName, setZipName] = useState("");
  const [threshold, selectThreshold] = useState();
  const [inputName, setInputName] = useState("");
  const [pageStatus, setPageStatus] = useState(1);
  const [images, setImages] = useState([]);
  const [csvData, setCsvData] = useState([]);
  const [uploadedProteins, setUploadedProteins] = useState([]);
  const [proteinStatus, setProteinStatus] = useState([]);

  const handleReset = () => {
    setFile(null);
    setDb(null);
    setZip(null);
    setChoice("");
    setMode("");
    setDbName("");
    setZipName("");
    setInputName("");
    axios.delete("http://localhost:8000/validate")
    .then((response) => {
      console.log(response);
      setPageStatus(1);
    })
    .catch((error) => {
      console.log(error);
    })
  }

  const handleManual = () => {
    setPageStatus(2);
    const formData = new FormData();
    formData.append("choice", choice);
    formData.append("threshold", threshold);

    axios.post("http://localhost:8000/processmanual", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      console.log(response);
      console.log(response.data.csv_files);
      console.log(response.data.image_files);
      setCsvData(response.data.csv_files);
      setImages(response.data.image_files);
      setPageStatus(3);
    })
    .catch((error) => {
      console.log(error);
    });
  }

  const validateFiles = () => {
    if (!zip || !db || !file) {
      alert("Please upload all the files");
      return;
    }

    const formData = new FormData();
    formData.append("zip_file", zip);
    formData.append("gz_file", db);
    formData.append("csv_file", file);
    formData.append("choice", choice);

    axios.post("http://localhost:8000/validate", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      setUploadedProteins(Object.keys(response.data));
      setProteinStatus(response.data);
    })
    .catch((error) => {
      console.log(error);
    })

  }

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    if (!file || !db) {
      alert("Please upload both the files");
      return;
    }

    formData.append("csv_file", file);
    formData.append("gz_file", db);
    formData.append("choice", choice);
    formData.append("threshold", threshold);

    setPageStatus(2);
    axios
      .post("http://localhost:8000/process", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        console.log(response);
        console.log(response.data.csv_files);
        console.log(response.data.image_files);
        setCsvData(response.data.csv_files);
        setImages(response.data.image_files);
        setPageStatus(3);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <div className="main-container">
      <h1 className="heading">XL-MS Tool Developed by IITB</h1>
      {pageStatus === 1 ? (
        <div className="form-container">
          <form action="post" onSubmit={handleSubmit}>
            <h2 style={{ marginBottom: "1.1rem" }}>
              For processing upload the input(.csv) and database(.gz) files
            </h2>
            

            {/* <input type="text" /> */}
            <label htmlFor="">Select linking type:</label>
            <select
              onChange={(e) => {
                setChoice(e.target.value);
              }}
              className="select"
              id=""
            >
              <option disabled selected>
                Choose from the list
              </option>
              <option value="inter">Interlink</option>
              <option value="intra">Intralink</option>
              <option value="intra">Looplink</option>
              <option disabled>Monolink (Coming Soon)</option>
              <option disabled>Multiple Links (Coming Soon)</option>
            </select>

            <label htmlFor="">Select Mode:</label>
            <select className="select" id="" onChange={(e) => setMode(e.target.value)}>
              <option disabled selected>
                Choose from the list
              </option>
              <option value="auto">Automated</option>
              <option value="manual">Manual</option>
            </select>

            <div className="input-container">
              <p style={{ marginRight: "1rem" }}>Threshold:</p>
              <input type="number" onChange={(e) => selectThreshold(e.target.value)} onWheel={(e) => e.target.blur()} />
            </div>

            <p style={{ marginBottom: "0.5rem" }}>Input CSV file:</p>
            <div className="input-container">
              <Button
                component="label"
                role={undefined}
                onChange={(e) => {
                  setFile(e.target.files[0]);
                  setInputName(e.target.files[0].name);
                }}
                variant="contained"
                tabIndex={-1}
                startIcon={<CloudUploadIcon />}
              >
                Upload input file
                <VisuallyHiddenInput type="file" />
              </Button>
              <p>{inputName}</p>
            </div>

            {/* <input
            type="file"
            name="gz-file"
            onChange={(e) => setDb(e.target.files[0])}
          /> */}
            <p style={{ marginBottom: "0.5rem" }}>Database file:</p>
            <div className="input-container">
              <Button
                component="label"
                role={undefined}
                onChange={(e) => {
                  setDb(e.target.files[0]);
                  setDbName(e.target.files[0].name);
                }}
                variant="contained"
                tabIndex={-1}
                startIcon={<CloudUploadIcon />}
              >
                Upload Database
                <VisuallyHiddenInput type="file" />
              </Button>
              <p>{dbName}</p>
            </div>

            <p style={{ marginBottom: "0.5rem" }}>Zip file for proteins:</p>
            <div className="input-container">
              <Button
                component="label"
                role={undefined}
                onChange={(e) => {
                  setZip(e.target.files[0]);
                  setZipName(e.target.files[0].name);
                }}
                disabled={mode !== "manual"}
                variant="contained"
                tabIndex={-1}
                startIcon={<CloudUploadIcon />}
              >
                Upload Zip file
                <VisuallyHiddenInput type="file" />
              </Button>
              <p>{zipName}</p>
            </div>

            {/* <button type="submit">Submit</button> */}
            <Button onClick={(e) => {
              if (mode === "manual"){
                setPageStatus(4);
                validateFiles();
              }
              else {
                handleSubmit(e);
              }   
              }} 
              variant="contained" color="success">
              {mode === "manual" ? "Validate zip files": "Start Processing"}
            </Button>
          </form>
        </div>
      ) : // </div>
      pageStatus === 2 ? (
        // <div className="processing">
        //   <img width={"50%"} src="./process.gif" alt="" />
        // </div>
        <Processing />
      ) :
      pageStatus === 4 ? (
        <div className="validation form-container">
          {/* <h2>Following are the files you uploaded: </h2> */}
          <h2>Uploaded Proteins: </h2>
          <ul>
            {uploadedProteins.map((protein, index) => (
              <li key={index}><h3 style={{fontWeight: 'normal'}}>{protein}</h3></li>
            ))}
          </ul>
          <h2>Following are the proteins that are not present in the input file or are incorrectly formatted:</h2>
          <ul>
            {uploadedProteins.map((protein, index) => (
              (!proteinStatus[protein]? <li key={index}>{protein}</li> : null)
              // <li key={index}>{protein}</li>
            ))}
          </ul>
          <Button sx={{marginRight: '1rem'}} onClick={handleManual} variant="contained" color="success">
            Start Processing
          </Button>
          <Button onClick={() => handleReset()} variant="contained" color="error">
            Resubmit Files
          </Button>
        </div>
      )
      : (
        <div className="result-container">
          <h2 className="small-heading">Relevant Plots</h2>
          <div className="image-list">
            {images.map((image, index) => (
              <img
                src={`http://localhost:8000/media/${choice}/${image.image_file.split("/")[2]}`}
                style={{ width: "400px", height: "300px", marginRight: "1rem" }}
                alt="image"
              />
            ))}
          </div>

          <div>
            <h2 className="small-heading">
              Following are the links to the output files:
            </h2>
            <div className="downloads">
              {csvData.map((csv, index) => (
                // <li key={index}>
                <a href={`http://localhost:8000/media/${choice}/${csv.csv_file.split("/")[2]}`} download>
                  {csv.csv_file.split("/")[2]}
                </a>
                // </li>
              ))}
            </div>
          </div>
          {/* <p>CSV Data:</p>
            <ul>
                {csvData && csvData.map((csv, index) => (
                    <li key={index}>
                        <ParseCSV link={csv.csv_file} />
                    </li>
                ))}
            </ul> */}
        </div>
      )}
    </div>
  );
};

export default Process;
