export default function DownloadCsvButton({ csvContent, fileName, label = "Download CSV" }) {
  function downloadCsv() {
    const downloadUrl = URL.createObjectURL(new Blob([csvContent], { type: "text/csv;charset=utf-8" }));
    const downloadLink = document.createElement("a");
    downloadLink.href = downloadUrl;
    downloadLink.download = fileName;
    downloadLink.click();
    URL.revokeObjectURL(downloadUrl);
  }

  return <button className="download-button" onClick={downloadCsv} type="button">{label}</button>;
}
