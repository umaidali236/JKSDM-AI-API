const mainButton = document.getElementById('mainButton');
const graphContainer = document.getElementById('graphContainer');

// Sample data structure with additional information for graph
const careerPaths = {
    "Science": {
        "Engineering": {
            "Computer Science": [],
            "Mechanical Engineering": []
        },
        "Medical": []
    },
    "Commerce": [],
    "Arts": []
};

mainButton.addEventListener('click', () => {
    mainButton.style.display = 'none';

    // Prepare data for graph visualization
    const graphData = [];
    // ... logic to convert careerPaths object into graph data format

    // Create the graph using D3.js or a similar library
    const svg = d3.select("#graphContainer")
        .append("svg")
        .attr("width", 800)
        .attr("height", 600);

    // ... D3.js code to create nodes, links, and layout

});


// ... (data preparation)

const simulation = d3.forceSimulation(graphData.nodes)
    .force("link", d3.forceLink(graphData.links).id(d => d.id))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

const link = svg.append("g")
    .attr("stroke", "#ccc")
    .selectAll("line")
    .data(graphData.links)
    .enter().append("line")
    .attr("stroke-width", d => Math.sqrt(d.value));

const node = svg.append("g")
    .attr("stroke", "#fff")
    .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(graphData.nodes)
    .enter().append("circle")
    .attr("r", 5)
    .call(drag(simulation));