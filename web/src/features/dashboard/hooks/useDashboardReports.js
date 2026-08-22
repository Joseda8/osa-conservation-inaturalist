import { useEffect, useState } from "react";

export function useDashboardReports(reports) {
  const [reportContents, setReportContents] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    Promise.all(reports.map((report) => fetch(`${import.meta.env.BASE_URL}data/${report.fileName}`).then((response) => {
      if (!response.ok) {
        throw new Error(`The ${report.label.toLowerCase()} report could not be loaded.`);
      }
      return response.text();
    })))
      .then((csvContents) => setReportContents(Object.fromEntries(reports.map((report, reportIndex) => [report.id, csvContents[reportIndex]]))))
      .catch((error) => setErrorMessage(error.message));
  }, [reports]);

  return { errorMessage, reportContents };
}
