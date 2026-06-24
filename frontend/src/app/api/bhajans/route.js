import { execFile } from "child_process";
import { promisify } from "util";
import path from "path";

export const dynamic = "force-dynamic";

const execFileAsync = promisify(execFile);

export async function GET(request) {
  try {
    const scriptPath = path.resolve(process.cwd(), "../backend/api_wrapper.py");
    const { stdout } = await execFileAsync("python", [scriptPath, "all"], { maxBuffer: 50 * 1024 * 1024 });
    const data = JSON.parse(stdout);
    return Response.json(data);
  } catch (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
}
