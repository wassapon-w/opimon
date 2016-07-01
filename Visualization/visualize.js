var data = {};

var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("get", url, true);
    xhr.responseType = "json";
    xhr.onload = function() {
      var status = xhr.status;
      if (status == 200) {
        callback(null, xhr.response);
      } else {
        callback(status);
      }
    };
    xhr.send();
};

getJSON('http://192.168.22.132:3000/flowmods', function(err, output){
    data["flowmods"] = output;
    // console.log(data["flowmods"]);
});

getJSON('http://192.168.22.132:3000/topology', function(err, output){
    data["switch"] = output["node"];
    data["connect"] = output["link"];
    visualize();
});

function visualize() {
  console.log(data);

  var color = d3.scaleOrdinal(d3.schemeCategory20);

  var canvas = document.querySelector("canvas"),
      context = canvas.getContext("2d"),
      width = canvas.width,
      height = canvas.height;

  var simulation = d3.forceSimulation()
      .force("link", d3.forceLink().id(function(d) { return d.id; }))
      .force("charge", d3.forceManyBody())
      .force("center", d3.forceCenter());

  simulation
      .nodes(data.switch)
      .on("tick", ticked);

  simulation.force("link")
      .links(data.connect);

  function ticked() {
    context.clearRect(0, 0, width, height);
    context.save();
    context.translate(width / 3, height / 3);

    context.beginPath();
    data.connect.forEach(drawLink);
    context.strokeStyle = "#aaa";
    context.stroke();

    context.beginPath();
    data.switch.forEach(drawNode);
    context.fillStyle = color(data.switch.forEach(function(d) { return d.id; }));
    context.fill();
    // context.strokeStyle = "#fff";
    // context.stroke();

    context.restore();
  }

  function drawLink(d) {
    context.moveTo(d.source.x, d.source.y);
    context.lineTo(d.target.x, d.target.y);
  }

  function drawNode(d) {
    context.moveTo(d.x + 100, d.y);
    context.arc(d.x, d.y, 10, 0, 2 * Math.PI);
  }
}
