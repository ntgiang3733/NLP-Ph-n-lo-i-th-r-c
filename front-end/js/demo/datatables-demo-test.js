// Call the dataTables jQuery plugin
$(document).ready(function() {
    fetch('http://localhost:5000/result')
        .then(response => response.json())
        .then(json => {
          handleTable(json)
        })
  });
  
  function handleTable(json) {
    console.log(json);
    let tr = "";
    let tbody = $("#tbody");
    for(let i=0; i<json.old_document_test.length; i++) {
      tr = "<tr><td>" + json.old_document_test[i] + "</td><td>" + json.label_test[i] + "</td><td>" + json.pred[i] + "</td></tr>";
      tbody.append(tr);
    }
    $('#dataTable').DataTable();
    $('#result').text(Number(json.result)*100 + ' %');
  }
  