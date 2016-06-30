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

  // var width = 960,
  //     height = 500;
  //
  // var color = d3.scale.category20();
  //
  // var force = d3.layout.force()
  //     .charge(-120)
  //     .linkDistance(30)
  //     .size([width, height]);
  //
  // var svg = d3.select("body").append("svg")
  //     .attr("width", width)
  //     .attr("height", height);
  //
  // force
  //     .nodes(data.switch)
  //     .links(data.connect)
  //     .start();
  //
  // var link = svg.selectAll(".link")
  //     .data(data.connect)
  //     .enter().append("line")
  //     .attr("class", "link")
  //     .style("stroke-width", function(d) { return 5 });
  //
  // var node = svg.selectAll(".node")
  //     .data(data.switch)
  //     .enter().append("circle")
  //     .attr("class", "node")
  //     .attr("r", 10)
  //     .style("fill", function(d) { return color(d.switch_id); });
  //     // .call(force.drag);
  //
  // node.append("title")
  //     .text(function(d) { return d.switch_id; });
  //
  // force.on("tick", function() {
  //   link.attr("x1", function(d) { return d.source.x; })
  //       .attr("y1", function(d) { return d.source.y; })
  //       .attr("x2", function(d) { return d.target.x; })
  //       .attr("y2", function(d) { return d.target.y; });
  //
  //   node.attr("cx", function(d) { return d.x; })
  //       .attr("cy", function(d) { return d.y; });
  // });

  // var color = d3.scaleCategory20();

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
    context.fill();
    // context.fillStyle = color(data.switch);
    context.strokeStyle = "#fff";
    context.stroke();

    context.restore();
  }

  function drawLink(d) {
    context.moveTo(d.source.x, d.source.y);
    context.lineTo(d.target.x, d.target.y);
  }

  function drawNode(d) {
    context.moveTo(d.x + 100, d.y);
    context.arc(d.x, d.y, 10, 0, 10 * Math.PI);
  }
}
