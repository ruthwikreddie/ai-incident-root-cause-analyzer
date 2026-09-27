import io
import textwrap

from reportlab.pdfgen import canvas

from ..schemas import IncidentAnalysis


def build_pdf(analysis: IncidentAnalysis) -> bytes:
    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)

    y = 800

    def write_line(text: str = "") -> None:
        nonlocal y

        lines = textwrap.wrap(
            str(text),
            width=90,
        ) or [""]

        for wrapped_line in lines:
            if y < 60:
                pdf.showPage()
                y = 800

            pdf.drawString(
                50,
                y,
                wrapped_line,
            )

            y -= 18

    write_line("AI Incident Root Cause Report")
    write_line()

    write_line("ROOT CAUSE")
    write_line(analysis.root_cause)
    write_line()

    write_line("SEVERITY")
    write_line(analysis.severity.upper())
    write_line()

    write_line("AFFECTED SERVICES")

    for service in analysis.affected_services:
        write_line(f"- {service}")

    write_line()

    write_line("FIX RECOMMENDATION")
    write_line(analysis.fix_recommendation)
    write_line()

    write_line("POSTMORTEM SUMMARY")
    write_line(analysis.postmortem_summary)

    pdf.save()

    buffer.seek(0)

    return buffer.read()
