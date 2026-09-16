
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

const port = 3000;

async function servePage(
    fileName: string,
    res: import("node:http").ServerResponse
) {
    try {
        const html = await readFile(
            join(
                process.cwd(),
                "src",
                "presentation",
                "pages",
                fileName
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
}

const server = createServer(async (req, res) => {

    if (req.method === "GET" && req.url === "/") {
        await servePage("display_features.html", res);
        return;
    }

    if (req.method === "GET" && req.url === "/login") {
        await servePage("login.html", res);
        return;
    }

    res.writeHead(404, {
        "Content-Type": "text/plain"
    });

    res.end("Not Found");
});

server.listen(port, "0.0.0.0", () => {
    console.log(
        `Frontend running on http://localhost:${port}`
    );
});

