import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

const port = 3000;

const server = createServer(async (req, res) => {
    if (req.url === "/" && req.method === "GET") {
        try {
            const html = await readFile(
                join(
                    process.cwd(),
                    "src",
                    "presentation",
                    "pages",
                    "display_features.html"
                ),
                "utf-8"
            );

            res.writeHead(200, {
                "Content-Type": "text/html; charset=utf-8"
            });

            res.end(html);
        } catch (error) {
            console.error(error);

            res.writeHead(500, {
                "Content-Type": "text/plain"
            });

            res.end("Failed to load frontend page");
        }

        return;
    }

    res.writeHead(404, {
        "Content-Type": "text/plain"
    });

    res.end("Not Found");
});

server.listen(port, "0.0.0.0", () => {
    console.log(`Frontend running on http://localhost:${port}`);
});


