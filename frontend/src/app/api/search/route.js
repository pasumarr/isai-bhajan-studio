import { execFile } from "child_process";
import { promisify } from "util";
import path from "path";

export const dynamic = "force-dynamic";

const execFileAsync = promisify(execFile);

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const q = searchParams.get("q") || "";
    const deity = searchParams.get("deity") || "";
    const raga = searchParams.get("raga") || "";
    const beat = searchParams.get("beat") || "";
    const tempo = searchParams.get("tempo") || "";
    const level = searchParams.get("level") || "";
    const language = searchParams.get("language") || "";
    const songtags = searchParams.get("songtags") || "";

    const scriptPath = path.resolve(process.cwd(), "../backend/api_wrapper.py");
    const { stdout } = await execFileAsync("python3", [
      scriptPath, "search", q, deity, raga, beat, tempo, level, language, songtags
    ], { maxBuffer: 50 * 1024 * 1024 });
    const data = JSON.parse(stdout);
    return Response.json(data);
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
