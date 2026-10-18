export const trend = {
  meta: {
    slug: "trend-to-line",
    title: "Every trend graph is a line graph",
    description: "Learners turn a table, a bar chart and pie charts over time into a line graph: draw the axes, dot the values, connect the dots.",
    tags: ["ielts", "writing-task-1", "trend-graph"],
  },
  config: {
    mode: "trend",
    target: "line_graph",
    caption: "Commuters by transport (%)",
    unit: "%",
    x: ["2000", "2005", "2010", "2015"],
    series: [
      { key: "car", label: "Car", values: [55, 48, 40, 28] },
      { key: "bus", label: "Bus", values: [30, 32, 35, 33] },
      { key: "bike", label: "Bike", values: [15, 20, 25, 39] },
    ],
    yMax: 60,
    yTicks: [0, 20, 40, 60],
    yName: "VALUE (%)",
    xName: "TIME →",
    tabs: [
      {
        id: "table", label: "Table", source: "table",
        steps: [
          { title: "Start with the table", desc: "Four years, three ways to get to work. The kind of table you'd type into Excel.", next: "Draw the axes →" },
          { title: "Draw two axes", desc: "Bottom axis = time (the years). Side axis = the value (%).", next: "Plot the dots →" },
          { title: "Turn every cell into a dot", desc: "Each number becomes one dot: find its year along the bottom, its value up the side.", next: "Connect the dots →" },
          { title: "Connect each row", desc: "One row = one line. Now the trend jumps out: cars fall, bikes climb right past them." },
        ],
      },
      {
        id: "bars", label: "Bar chart", source: "bars",
        steps: [
          { title: "Start with the bar chart", desc: "Same data, new skin. Each colour is one type of transport.", next: "Check the axes →" },
          { title: "It already has the axes", desc: "Time along the bottom, value up the side. A bar chart over time is already on a line graph's axes, so nothing to draw.", next: "Mark the tips →" },
          { title: "Mark the tip of every bar", desc: "Put a dot right on top of each bar. That dot is exactly where the line graph's dot goes.", next: "Connect the tips →" },
          { title: "Connect tips of the same colour", desc: "Fade the bars and… line graph. A bar chart over time is just a line graph that hasn't been connected yet." },
        ],
      },
      {
        id: "pie", label: "Pie charts", source: "pie",
        steps: [
          { title: "Start with the pie charts", desc: "One pie per year. Every pie adds up to 100%.", next: "Draw the axes →" },
          { title: "Draw two axes", desc: "Time along the bottom, percentage up the side. Exactly like the table.", next: "Follow each slice →" },
          { title: "Follow one slice across the years", desc: "Take the same slice (say, Car) in every pie. Each one becomes a dot.", next: "Connect the dots →" },
          { title: "Connect each slice's dots", desc: "Pies over time = a table in disguise = a line graph." },
        ],
      },
    ],
  },
};

export const staticGraph = {
  meta: {
    slug: "static-to-bar",
    title: "Every static graph is a bar chart",
    description: "Learners turn a one-year table and a pie chart into a bar chart: draw the axes, dot the values, let the bars rise.",
    tags: ["ielts", "writing-task-1", "static-graph"],
  },
  config: {
    mode: "static",
    target: "bar_chart",
    caption: "Household spending, 2020 (%)",
    unit: "%",
    valueLabel: "Share",
    x: ["Housing", "Food", "Transport", "Leisure", "Other"],
    values: [34, 24, 17, 14, 11],
    yMax: 40,
    yTicks: [0, 10, 20, 30, 40],
    yName: "VALUE (%)",
    xName: "CATEGORIES (not time!) →",
    tabs: [
      {
        id: "table", label: "Table", source: "table",
        steps: [
          { title: "Start with the table", desc: "One year only: 2020. No time to follow, just five categories to compare.", next: "Draw the axes →" },
          { title: "Draw two axes", desc: "Plot twist: the bottom axis is NOT time this time. It holds the categories. The side axis holds the value (%).", next: "Plot the dots →" },
          { title: "Turn every cell into a dot", desc: "Each value sits right above its own category.", next: "Raise the bars →" },
          { title: "Let the bars rise", desc: "Fill from the axis up to each dot: bar chart. Now comparing is easy: Housing is the biggest, Other the smallest." },
        ],
      },
      {
        id: "pie", label: "Pie chart", source: "pie",
        steps: [
          { title: "Start with the pie chart", desc: "One pie, one moment in time. The slices add up to 100%.", next: "Draw the axes →" },
          { title: "Draw two axes", desc: "One category per slice along the bottom, percentage up the side.", next: "Plot the dots →" },
          { title: "Turn every slice into a dot", desc: "The size of each slice becomes the height of its dot.", next: "Raise the bars →" },
          { title: "Let the bars rise", desc: "A pie chart is just a bar chart rolled into a circle. Bars make the ranking obvious." },
        ],
      },
    ],
  },
};
