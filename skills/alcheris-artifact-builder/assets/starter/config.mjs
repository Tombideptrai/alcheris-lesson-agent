// Content for each artifact built from this engine. Add more entries to build
// a family of artifacts from one engine (see examples/graph-skins/configs.mjs).
export const artifacts = [
  {
    meta: {
      slug: "starter-bars",
      title: "From numbers to bars",
      description: "Learners watch three numbers become a bar chart, then say which bar is tallest.",
      preset: "portrait", // "portrait" (9:16) or "square" (1:1)
    },
    config: {
      fitDrawing: true, // drawing follows the stage shape; redraws on resize
      values: [
        { label: "A", value: 30 },
        { label: "B", value: 55 },
        { label: "C", value: 20 },
      ],
      max: 60,
      tabs: [
        {
          id: "build",
          label: "Build it",
          steps: [
            { title: "Start with the numbers", desc: "Three values. Nothing drawn yet.", next: "Draw the axis →" },
            { title: "Draw the axis", desc: "One line along the bottom: every bar stands on it.", next: "Raise the bars →" },
            { title: "Raise the bars", desc: "Each bar's height is its value.", next: "Check yourself →" },
            {
              title: "Your turn",
              desc: "Read the chart, not the numbers.",
              check: {
                prompt: "Which bar shows the biggest value?",
                options: ["A", "B", "C"],
                answer: 1,
                hints: { 0: "A is tall, but compare it with the middle bar.", 2: "C is the shortest bar." },
                explain: "B: the tallest bar always shows the biggest value.",
              },
            },
          ],
        },
      ],
    },
  },
];
