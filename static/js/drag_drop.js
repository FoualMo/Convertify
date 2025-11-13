const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("fileInput");

    // Clique => ouvrir le sélecteur
    dropArea.addEventListener("click", () => fileInput.click());

    // Highlight
    ["dragenter", "dragover"].forEach(eventName => {
        dropArea.addEventListener(eventName, e => {
            e.preventDefault();
            dropArea.classList.add("highlight");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropArea.addEventListener(eventName, e => {
            e.preventDefault();
            dropArea.classList.remove("highlight");
        });
    });

    // Handle drop
    dropArea.addEventListener("drop", e => {
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // Handle normal input
    fileInput.addEventListener("change", () => {
        handleFile(fileInput.files[0]);
    });

    function handleFile(file) {
        console.log("Fichier sélectionné :", file);
        // Ici tu fais ton upload AJAX ou tu remplis un formulaire
    }

