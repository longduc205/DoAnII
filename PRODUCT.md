# Product

## Register

product

## Users

Security students and early-career developers building academic projects around web application security. They scan intentionally vulnerable targets (DVWA, WebGoat) to learn how SQL Injection and XSS attacks work. They care about understanding results, not just collecting them. Context: working on a university laptop, likely in a well-lit room or library, scanning local Docker targets while writing their thesis.

The user base will grow as the project evolves through Đồ Án III and graduation thesis into a more complete security assessment platform for developers and junior security researchers.

## Product Purpose

An AI-integrated web vulnerability scanner that combines rule-based testing with machine-learning-assisted response classification. The scanner crawls target web applications, identifies forms and input parameters, performs automated vulnerability tests (SQL Injection, XSS), and uses a trained ML model to classify server responses as normal or suspicious.

Success looks like: a student can paste a URL, watch the scan progress, and walk away with a clear understanding of what was found, why it matters, and how confident the AI is about each finding.

## Brand Personality

Refined, Confident, Clear.

The interface should feel like a well-made instrument: precise, trustworthy, and satisfying to use. No unnecessary decoration, but every detail considered. The kind of tool that makes the user feel capable and informed, not overwhelmed.

## Anti-references

- **Hollywood hacker aesthetic.** No green-on-black terminals, no Matrix rain, no neon-on-dark "cyber" visuals. Security tools don't need to look dangerous to be taken seriously.
- **Overcrowded Homepages.** No Grafana-style walls of charts competing for attention. This tool has a focused workflow, not a monitoring surface.
- **Generic SaaS templates.** No hero-metric cards with big numbers and tiny labels. No identical card grids with icon + heading + description repeated six times.

## Design Principles

1. **Clarity over complexity.** Security data is inherently dense. The interface earns trust by making findings immediately understandable, not by exposing every raw detail at once.
2. **Confidence through craft.** Subtle polish (considered spacing, smooth transitions, typographic hierarchy) signals reliability. A tool that looks precise feels precise.
3. **Progressive depth.** Simple at the surface, detailed when you ask for it. Scan summary first, then drill into individual findings, then raw response data.
4. **Data speaks first.** Scan results and AI classifications are the hero, not the chrome around them. Every UI element exists to support comprehension of findings.
5. **Evolve gracefully.** The design system must accommodate new vulnerability types, new AI capabilities, and new workflows as the project grows through Đồ Án III and graduation thesis.

## Accessibility & Inclusion

WCAG 2.1 AA as baseline. No specific accommodations required at this stage, but maintain sufficient color contrast ratios and logical heading structure to keep the door open for future accessibility work.
