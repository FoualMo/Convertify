document.getElementById("convertForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);

  const response = await fetch("/convert", {
    method: "POST",
    body: formData
  });

  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "converted_file";
    a.click();
  } else {
    alert("Erreur lors de la conversion !");
  }
});
