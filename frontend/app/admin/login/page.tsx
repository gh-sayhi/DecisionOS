"use client";

import { Lock, LogIn } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { TopNav } from "@/components/top-nav";

export default function AdminLoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      if (!response.ok) {
        throw new Error("账号或密码错误");
      }
      const data = await response.json();
      localStorage.setItem("admin_token", data.access_token);
      router.push("/admin");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <TopNav title="后台登录" icon={<Lock size={18} />} />
      <div className="login-shell">
        <section className="panel login-panel">
          <div className="panel-header">
            <h1 className="panel-title">管理员登录</h1>
            <p className="panel-subtitle">默认开发账号 admin / admin123，可通过后端环境变量修改。</p>
          </div>
          <form className="form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="username">账号</label>
              <input id="username" value={username} onChange={(event) => setUsername(event.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="password">密码</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>
            {error ? <div className="error">{error}</div> : null}
            <button className="submit" disabled={loading} type="submit">
              <LogIn size={16} />
              {loading ? "登录中" : "登录后台"}
            </button>
          </form>
        </section>
      </div>
    </main>
  );
}
