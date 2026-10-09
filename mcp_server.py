"""MCP server exposing clinic tools. Run standalone: python mcp_server.py (stdio transport)."""
import re
from mcp.server.fastmcp import FastMCP
from db import connect

mcp = FastMCP("clinic-tools")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")


@mcp.tool()
def list_doctors(specialty: str = "") -> str:
    """List doctors. Optionally filter by specialty keyword (e.g. 'cardiology', 'pediatrics') or doctor name."""
    conn = connect()
    rows = conn.execute(
        "SELECT id, name, specialty FROM doctors WHERE specialty LIKE ? OR name LIKE ?",
        (f"%{specialty}%", f"%{specialty}%"),
    ).fetchall()
    conn.close()
    if not rows:
        return "No doctors found for that query."
    return "\n".join(f"id={r['id']}: {r['name']} ({r['specialty']})" for r in rows)


@mcp.tool()
def get_available_slots(doctor_id: int, date: str) -> str:
    """Get free appointment times for a doctor on a date (format YYYY-MM-DD)."""
    if not DATE_RE.match(date):
        return "Error: date must be in YYYY-MM-DD format."
    conn = connect()
    if not conn.execute("SELECT 1 FROM doctors WHERE id=?", (doctor_id,)).fetchone():
        conn.close()
        return f"Error: doctor {doctor_id} not found."
    rows = conn.execute(
        "SELECT time FROM slots WHERE doctor_id=? AND date=? AND booked=0 ORDER BY time", (doctor_id, date)
    ).fetchall()
    conn.close()
    if not rows:
        return f"No free slots for doctor {doctor_id} on {date}."
    return f"Free slots on {date}: " + ", ".join(r["time"] for r in rows)


@mcp.tool()
def book_appointment(patient_name: str, doctor_id: int, date: str, time: str) -> str:
    """Book an appointment. Needs patient name, doctor id, date (YYYY-MM-DD) and time (HH:MM)."""
    if not patient_name.strip():
        return "Error: patient name is required."
    if not DATE_RE.match(date) or not TIME_RE.match(time):
        return "Error: use date YYYY-MM-DD and time HH:MM."
    conn = connect()
    slot = conn.execute(
        "SELECT booked FROM slots WHERE doctor_id=? AND date=? AND time=?", (doctor_id, date, time)
    ).fetchone()
    if slot is None:
        conn.close()
        return "Error: that slot does not exist."
    if slot["booked"]:
        conn.close()
        return "Error: that slot is already booked."
    cur = conn.execute(
        "INSERT INTO appointments (patient_name, doctor_id, date, time) VALUES (?,?,?,?)",
        (patient_name.strip(), doctor_id, date, time),
    )
    conn.execute("UPDATE slots SET booked=1 WHERE doctor_id=? AND date=? AND time=?", (doctor_id, date, time))
    conn.commit()
    appt_id = cur.lastrowid
    conn.close()
    return f"Confirmed: appointment id={appt_id} for {patient_name.strip()} on {date} at {time}."


@mcp.tool()
def cancel_appointment(appointment_id: int) -> str:
    """Cancel an appointment by its id and free the slot."""
    conn = connect()
    appt = conn.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
    if appt is None:
        conn.close()
        return f"Error: appointment {appointment_id} not found."
    if appt["status"] == "cancelled":
        conn.close()
        return "Appointment is already cancelled."
    conn.execute("UPDATE appointments SET status='cancelled' WHERE id=?", (appointment_id,))
    conn.execute(
        "UPDATE slots SET booked=0 WHERE doctor_id=? AND date=? AND time=?",
        (appt["doctor_id"], appt["date"], appt["time"]),
    )
    conn.commit()
    conn.close()
    return f"Appointment {appointment_id} cancelled."


@mcp.tool()
def get_appointment(appointment_id: int) -> str:
    """Look up an appointment by id."""
    conn = connect()
    a = conn.execute("SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
    conn.close()
    if a is None:
        return f"Error: appointment {appointment_id} not found."
    return (f"Appointment {a['id']}: {a['patient_name']} with doctor {a['doctor_id']} "
            f"on {a['date']} at {a['time']} (status: {a['status']}).")


if __name__ == "__main__":
    mcp.run()
