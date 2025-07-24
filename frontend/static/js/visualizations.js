// Interactive Visualizations for Timeline and Protocol Maps

// Function to render a timeline-based case viewer
function renderTimeline(caseData) {
    const container = document.getElementById('timeline-container');
    container.innerHTML = ''; // Clear existing content

    caseData.events.forEach(event => {
        const eventElement = document.createElement('div');
        eventElement.className = 'timeline-event';
        eventElement.innerHTML = `
            <div class="event-date">${event.date}</div>
            <div class="event-description">${event.description}</div>
        `;
        container.appendChild(eventElement);
    });
}

// Function to render a protocol network map
function renderProtocolMap(protocolData) {
    const container = document.getElementById('protocol-map-container');
    container.innerHTML = ''; // Clear existing content

    const svg = d3.select(container)
        .append('svg')
        .attr('width', 800)
        .attr('height', 600);

    const simulation = d3.forceSimulation(protocolData.nodes)
        .force('link', d3.forceLink(protocolData.links).id(d => d.id))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(400, 300));

    const link = svg.append('g')
        .selectAll('line')
        .data(protocolData.links)
        .enter().append('line')
        .attr('stroke-width', 2);

    const node = svg.append('g')
        .selectAll('circle')
        .data(protocolData.nodes)
        .enter().append('circle')
        .attr('r', 5)
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));

    node.append('title')
        .text(d => d.name);

    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
    });

    function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Export functions for use in other modules
export { renderTimeline, renderProtocolMap };
