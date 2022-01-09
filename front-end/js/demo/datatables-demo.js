// Call the dataTables jQuery plugin
$(document).ready(function() {
  fetch('http://localhost:5000/result')
      .then(response => response.json())
      .then(json => {
        handleTable(json)
      })
});

function handleTable(json) {
  let tr = "";
  let tbody = $("#tbody");
  for(let i=0; i<json.document.length; i++) {
    tr = "<tr><td>" + json.old_document[i] + "</td><td>" + json.document[i] + "</td><td>" + json.label[i] + "</td></tr>";
    tbody.append(tr);
  }
  $('#dataTable').DataTable();
}
