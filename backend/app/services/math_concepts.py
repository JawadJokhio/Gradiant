"""
O-Level Mathematics Concepts Dictionary
Covers Cambridge IGCSE / O-Level syllabus topics (0580 / 4024)
"""

MATH_CONCEPTS = {
    # ── Number ────────────────────────────────────────────────────────────────
    "addition": {
        "title": "Addition",
        "explanation": (
            "Addition is the process of combining two or more numbers to get a total. "
            "The numbers being added are called addends and the result is the sum. "
            "The order doesn't matter: a + b = b + a (commutative property)."
        ),
        "example": "23 + 47 = 70  |  3.5 + 1.2 = 4.7",
    },
    "subtraction": {
        "title": "Subtraction",
        "explanation": (
            "Subtraction finds the difference between two numbers. "
            "a − b asks 'how much more is a than b?' Unlike addition, order matters."
        ),
        "example": "85 − 37 = 48  |  10.0 − 3.6 = 6.4",
    },
    "multiplication": {
        "title": "Multiplication",
        "explanation": (
            "Multiplication is repeated addition. a × b means add a to itself b times. "
            "The result is called the product. It is commutative: a × b = b × a."
        ),
        "example": "6 × 7 = 42  |  2.5 × 4 = 10",
    },
    "division": {
        "title": "Division",
        "explanation": (
            "Division splits a number into equal parts. a ÷ b asks 'how many groups of b fit into a?' "
            "The result is the quotient. Division by zero is undefined."
        ),
        "example": "48 ÷ 6 = 8  |  15 ÷ 4 = 3.75",
    },
    "bodmas": {
        "title": "Order of Operations (BODMAS / BIDMAS)",
        "explanation": (
            "BODMAS defines the order to evaluate expressions: "
            "Brackets → Orders (powers/roots) → Division → Multiplication → Addition → Subtraction. "
            "Always work left-to-right within the same priority level."
        ),
        "example": "3 + 4 × 2 = 3 + 8 = 11  (multiply first, not 14)",
    },
    "fractions": {
        "title": "Fractions",
        "explanation": (
            "A fraction represents part of a whole: numerator/denominator. "
            "To add/subtract fractions find a common denominator. "
            "To multiply: multiply numerators and denominators separately. "
            "To divide: multiply by the reciprocal."
        ),
        "example": "1/2 + 1/3 = 3/6 + 2/6 = 5/6  |  2/3 ÷ 4/5 = 2/3 × 5/4 = 10/12 = 5/6",
    },
    "percentages": {
        "title": "Percentages",
        "explanation": (
            "A percentage expresses a number as parts per hundred. "
            "To find x% of y: multiply y × x/100. "
            "Percentage change = (change ÷ original) × 100."
        ),
        "example": "20% of 150 = 150 × 20/100 = 30  |  Increase 80 by 15%: 80 × 1.15 = 92",
    },
    "ratio": {
        "title": "Ratio",
        "explanation": (
            "A ratio compares two quantities of the same kind. "
            "a : b means for every a of one thing there are b of another. "
            "Simplify by dividing both parts by their HCF."
        ),
        "example": "12 : 8 simplifies to 3 : 2  |  Share 60 in ratio 2:3 → 24 and 36",
    },
    "proportion": {
        "title": "Proportion",
        "explanation": (
            "Direct proportion: as one quantity increases, the other increases at the same rate (y = kx). "
            "Inverse proportion: as one increases, the other decreases (y = k/x). "
            "Use the unitary method: find the value for 1, then scale."
        ),
        "example": "5 pens cost $3.50 → 1 pen costs $0.70 → 12 pens cost $8.40",
    },
    "hcf": {
        "title": "Highest Common Factor (HCF)",
        "explanation": (
            "The HCF of two numbers is the largest number that divides both exactly. "
            "Find it by listing factors or using prime factorisation."
        ),
        "example": "HCF(12, 18): factors of 12={1,2,3,4,6,12}, of 18={1,2,3,6,9,18} → HCF = 6",
    },
    "lcm": {
        "title": "Lowest Common Multiple (LCM)",
        "explanation": (
            "The LCM is the smallest positive number that is a multiple of both given numbers. "
            "Use prime factorisation: take each prime to its highest power."
        ),
        "example": "LCM(4, 6) = 12  |  LCM(12, 18) = 36",
    },
    "prime_factorisation": {
        "title": "Prime Factorisation",
        "explanation": (
            "Writing a number as a product of its prime factors. "
            "Use a factor tree or repeated division by the smallest prime."
        ),
        "example": "360 = 2³ × 3² × 5",
    },
    "standard_form": {
        "title": "Standard Form (Scientific Notation)",
        "explanation": (
            "Standard form writes a number as a × 10ⁿ where 1 ≤ a < 10 and n is an integer. "
            "Large numbers: positive n. Small decimals: negative n."
        ),
        "example": "4500 = 4.5 × 10³  |  0.0032 = 3.2 × 10⁻³",
    },
    "rounding": {
        "title": "Rounding & Significant Figures",
        "explanation": (
            "To round to n decimal places, look at the (n+1)th digit: if ≥5 round up, else round down. "
            "Significant figures start from the first non-zero digit."
        ),
        "example": "3.7462 to 2 d.p. = 3.75  |  0.004682 to 3 s.f. = 0.00468",
    },
    "square_root": {
        "title": "Square Root",
        "explanation": (
            "The square root of x (written √x) is the number y such that y² = x. "
            "Every positive number has two square roots: +√x and −√x. "
            "√x is defined only for x ≥ 0 in real numbers."
        ),
        "example": "√49 = 7  |  √2 ≈ 1.414",
    },
    "indices": {
        "title": "Indices (Powers / Exponents)",
        "explanation": (
            "aⁿ means multiply a by itself n times. Key laws: "
            "aᵐ × aⁿ = aᵐ⁺ⁿ, aᵐ ÷ aⁿ = aᵐ⁻ⁿ, (aᵐ)ⁿ = aᵐⁿ, a⁰ = 1, a⁻ⁿ = 1/aⁿ, a^(1/n) = ⁿ√a."
        ),
        "example": "2³ × 2⁴ = 2⁷ = 128  |  8^(2/3) = (∛8)² = 2² = 4",
    },

    # ── Algebra ───────────────────────────────────────────────────────────────
    "expanding_brackets": {
        "title": "Expanding Brackets",
        "explanation": (
            "Multiply every term inside the bracket by the term outside. "
            "For double brackets use FOIL: First, Outer, Inner, Last."
        ),
        "example": "3(x + 4) = 3x + 12  |  (x+2)(x+3) = x² + 5x + 6",
    },
    "factorisation": {
        "title": "Factorisation",
        "explanation": (
            "The reverse of expanding brackets. Find common factors and take them outside. "
            "For quadratics: find two numbers that multiply to ac and add to b (ax² + bx + c)."
        ),
        "example": "6x² + 9x = 3x(2x + 3)  |  x² + 5x + 6 = (x+2)(x+3)",
    },
    "quadratic_formula": {
        "title": "Quadratic Formula",
        "explanation": (
            "For ax² + bx + c = 0, the solutions are: x = (−b ± √(b²−4ac)) / (2a). "
            "The discriminant b²−4ac tells you: >0 two real roots, =0 one repeated root, <0 no real roots."
        ),
        "example": "x²−5x+6=0: x = (5 ± √(25−24))/2 = (5 ± 1)/2 → x=3 or x=2",
    },
    "completing_the_square": {
        "title": "Completing the Square",
        "explanation": (
            "Rewrite ax² + bx + c in the form a(x + p)² + q. "
            "Step 1: factor out a. Step 2: add and subtract (b/2a)² inside. "
            "Useful for finding vertex of a parabola."
        ),
        "example": "x² + 6x + 5 = (x+3)² − 9 + 5 = (x+3)² − 4",
    },
    "linear_equations": {
        "title": "Solving Linear Equations",
        "explanation": (
            "Isolate the unknown by performing the same operation on both sides. "
            "Aim: get x alone on one side. Work step-by-step, keeping the equation balanced."
        ),
        "example": "3x − 7 = 14 → 3x = 21 → x = 7",
    },
    "simultaneous_equations": {
        "title": "Simultaneous Equations",
        "explanation": (
            "Two equations with two unknowns. Methods: elimination (multiply to match a coefficient, then add/subtract) "
            "or substitution (express one variable in terms of the other and substitute)."
        ),
        "example": "2x+y=7 and x−y=2 → add: 3x=9 → x=3, y=1",
    },
    "inequalities": {
        "title": "Inequalities",
        "explanation": (
            "Solve like an equation but remember: multiplying or dividing by a negative number reverses the inequality sign. "
            "Represent solutions on a number line; use open circles for strict inequalities."
        ),
        "example": "2x − 3 > 7 → 2x > 10 → x > 5",
    },
    "algebraic_fractions": {
        "title": "Algebraic Fractions",
        "explanation": (
            "Simplify by factorising numerator and denominator then cancelling common factors. "
            "Add/subtract: find a common denominator. Multiply: multiply straight across."
        ),
        "example": "(x²−4)/(x+2) = (x+2)(x−2)/(x+2) = x−2",
    },
    "sequences": {
        "title": "Sequences & nth Term",
        "explanation": (
            "Arithmetic sequence: common difference d, nth term = a + (n−1)d. "
            "Geometric sequence: common ratio r, nth term = arⁿ⁻¹. "
            "Find the nth term rule by examining differences."
        ),
        "example": "3, 7, 11, 15, … → d=4, nth term = 4n−1  →  10th term = 39",
    },
    "functions": {
        "title": "Functions",
        "explanation": (
            "A function f maps each input x to exactly one output f(x). "
            "Composite function: fg(x) = f(g(x)) — apply g first, then f. "
            "Inverse function f⁻¹(x): swap x and y, then rearrange."
        ),
        "example": "f(x)=2x+1, g(x)=x²  →  fg(3)=f(9)=19  |  f⁻¹(x)=(x−1)/2",
    },

    # ── Geometry ──────────────────────────────────────────────────────────────
    "area": {
        "title": "Area",
        "explanation": (
            "Area measures the amount of space inside a 2D shape. Common formulas: "
            "Rectangle = l × w, Triangle = ½bh, Circle = πr², Trapezium = ½(a+b)h, Parallelogram = bh."
        ),
        "example": "Rectangle 8cm × 5cm → Area = 40 cm²  |  Circle r=3: Area = 9π ≈ 28.27 cm²",
    },
    "perimeter": {
        "title": "Perimeter",
        "explanation": (
            "Perimeter is the total distance around the outside of a 2D shape. "
            "For a circle, the perimeter is called the circumference: C = 2πr."
        ),
        "example": "Rectangle 8×5: P = 2(8+5) = 26 cm  |  Circle r=3: C = 6π ≈ 18.85 cm",
    },
    "volume": {
        "title": "Volume",
        "explanation": (
            "Volume measures 3D space. Common formulas: Cuboid = lwh, Cylinder = πr²h, "
            "Cone = ⅓πr²h, Sphere = 4/3πr³, Prism = cross-section area × length."
        ),
        "example": "Cylinder r=2, h=5: V = π×4×5 = 20π ≈ 62.83 cm³",
    },
    "pythagoras": {
        "title": "Pythagoras' Theorem",
        "explanation": (
            "In a right-angled triangle, the square of the hypotenuse equals the sum of the squares of the other two sides: "
            "a² + b² = c² where c is the hypotenuse (longest side, opposite the right angle)."
        ),
        "example": "a=3, b=4 → c² = 9+16 = 25 → c = 5",
    },
    "angles": {
        "title": "Angle Properties",
        "explanation": (
            "Key rules: angles on a straight line = 180°, angles around a point = 360°, "
            "vertically opposite angles are equal. In a triangle: angles sum to 180°. "
            "In a quadrilateral: angles sum to 360°."
        ),
        "example": "Two angles of a triangle are 65° and 75° → third angle = 180−65−75 = 40°",
    },
    "parallel_lines": {
        "title": "Parallel Lines & Transversals",
        "explanation": (
            "When a transversal crosses parallel lines: alternate angles are equal (Z-angles), "
            "corresponding angles are equal (F-angles), co-interior angles add up to 180° (C-angles)."
        ),
        "example": "If alternate angles: both equal 55°  |  Co-interior: 65° + 115° = 180°",
    },
    "circle_theorems": {
        "title": "Circle Theorems",
        "explanation": (
            "Key theorems: angle at centre = 2 × angle at circumference (same arc); "
            "angles in the same segment are equal; angle in semicircle = 90°; "
            "opposite angles in a cyclic quadrilateral sum to 180°; tangent is perpendicular to radius."
        ),
        "example": "Central angle 80° → inscribed angle on same arc = 40°",
    },
    "similarity": {
        "title": "Similar Shapes",
        "explanation": (
            "Similar shapes have the same angles and proportional sides. "
            "If the linear scale factor is k: area scale factor = k², volume scale factor = k³."
        ),
        "example": "Similar triangles, sides 3 and 6 → scale factor 2, area ratio 4:1",
    },
    "congruence": {
        "title": "Congruent Shapes",
        "explanation": (
            "Congruent shapes are identical in shape and size. "
            "Tests for congruent triangles: SSS, SAS, ASA, AAS, RHS."
        ),
        "example": "Two triangles with sides 3,4,5 are congruent by SSS",
    },
    "transformations": {
        "title": "Transformations",
        "explanation": (
            "Four main types: Translation (shift by vector), Reflection (flip over line), "
            "Rotation (turn around point by angle), Enlargement (scale by factor from centre). "
            "Describe each transformation fully."
        ),
        "example": "Enlargement scale factor 2, centre (0,0): (3,4) → (6,8)",
    },
    "vectors": {
        "title": "Vectors",
        "explanation": (
            "A vector has magnitude and direction. Written as column vector (x, y) or bold a. "
            "Addition: add components. Scalar multiplication: multiply each component. "
            "Magnitude |a| = √(x² + y²)."
        ),
        "example": "a=(3,4), |a|=5  |  2a=(6,8)  |  a+b=(3+1, 4+2)=(4,6)",
    },

    # ── Trigonometry ──────────────────────────────────────────────────────────
    "trigonometry": {
        "title": "Trigonometry (SOH-CAH-TOA)",
        "explanation": (
            "In a right-angled triangle: sin θ = Opposite/Hypotenuse, cos θ = Adjacent/Hypotenuse, tan θ = Opposite/Adjacent. "
            "Use SOH-CAH-TOA to remember the ratios."
        ),
        "example": "θ=30°, hyp=10 → opposite = 10 × sin30° = 10 × 0.5 = 5",
    },
    "sine_rule": {
        "title": "Sine Rule",
        "explanation": (
            "In any triangle: a/sinA = b/sinB = c/sinC. "
            "Use when you know: two angles and a side, or two sides and a non-included angle."
        ),
        "example": "a=7, A=40°, B=60° → b = 7 × sin60°/sin40° ≈ 9.42",
    },
    "cosine_rule": {
        "title": "Cosine Rule",
        "explanation": (
            "In any triangle: a² = b² + c² − 2bc cosA. "
            "Rearranged for angle: cosA = (b²+c²−a²)/(2bc). "
            "Use when you know: all three sides, or two sides and the included angle."
        ),
        "example": "b=5, c=7, A=60° → a² = 25+49−2(35)(0.5) = 39 → a ≈ 6.24",
    },
    "bearing": {
        "title": "Bearings",
        "explanation": (
            "A bearing is a direction measured clockwise from North, written as a 3-digit number. "
            "Back bearing = bearing ± 180°. Draw a diagram and use trigonometry to solve bearing problems."
        ),
        "example": "Bearing 065° means 65° clockwise from North (NE direction).",
    },

    # ── Graphs ────────────────────────────────────────────────────────────────
    "gradient": {
        "title": "Gradient (Slope)",
        "explanation": (
            "Gradient = rise/run = (y₂−y₁)/(x₂−x₁). "
            "Positive gradient: line goes uphill left-to-right. "
            "Negative gradient: downhill. Zero gradient: horizontal. Undefined: vertical."
        ),
        "example": "Points (1,2) and (4,8) → gradient = (8−2)/(4−1) = 6/3 = 2",
    },
    "y_intercept": {
        "title": "y-Intercept",
        "explanation": (
            "The y-intercept is where a line crosses the y-axis (x = 0). "
            "In y = mx + c, c is the y-intercept. Set x = 0 and solve for y."
        ),
        "example": "y = 3x + 5 → y-intercept = 5  (point (0, 5))",
    },
    "straight_line_graph": {
        "title": "Straight Line Graphs (y = mx + c)",
        "explanation": (
            "m is the gradient, c is the y-intercept. "
            "To draw: plot the y-intercept, then use gradient to find a second point. "
            "Parallel lines have equal gradients. Perpendicular lines: m₁ × m₂ = −1."
        ),
        "example": "y=2x+1: plot (0,1), move right 1 up 2 → (1,3). Draw line.",
    },
    "quadratic_graph": {
        "title": "Quadratic Graphs",
        "explanation": (
            "y = ax² + bx + c gives a parabola. Positive a: U-shape (minimum). "
            "Negative a: ∩-shape (maximum). Vertex at x = −b/(2a). "
            "Roots = x-intercepts (where y=0)."
        ),
        "example": "y=x²−4: vertex at (0,−4), crosses x-axis at x=±2",
    },
    "distance_time_graph": {
        "title": "Distance-Time Graph",
        "explanation": (
            "Gradient = speed. Horizontal line = stationary. "
            "Steeper line = greater speed. "
            "Area under a speed-time graph = distance."
        ),
        "example": "Line from (0,0) to (4,20): speed = 20/4 = 5 m/s",
    },

    # ── Statistics ────────────────────────────────────────────────────────────
    "mean": {
        "title": "Mean (Arithmetic Average)",
        "explanation": (
            "Mean = sum of all values ÷ number of values. "
            "For grouped data: mean ≈ Σ(midpoint × frequency) ÷ Σfrequency."
        ),
        "example": "Data: 4, 7, 9, 12 → mean = 32 ÷ 4 = 8",
    },
    "median": {
        "title": "Median",
        "explanation": (
            "The median is the middle value when data is sorted. "
            "For n values: median is at position (n+1)/2. "
            "For even n, average the two middle values."
        ),
        "example": "Sorted: 3, 5, 7, 9, 11 → median = 7 (3rd of 5)",
    },
    "mode": {
        "title": "Mode",
        "explanation": (
            "The mode is the most frequently occurring value. "
            "A data set can have one mode (unimodal), two modes (bimodal), or no mode."
        ),
        "example": "Data: 2, 3, 3, 5, 7, 3 → mode = 3",
    },
    "range": {
        "title": "Range",
        "explanation": (
            "Range = largest value − smallest value. "
            "It measures how spread out the data is. "
            "A large range means more variability."
        ),
        "example": "Data: 3, 7, 12, 19 → range = 19 − 3 = 16",
    },
    "probability": {
        "title": "Probability",
        "explanation": (
            "P(event) = number of favourable outcomes ÷ total possible outcomes. "
            "0 ≤ P ≤ 1. P(A') = 1 − P(A). "
            "Combined events: P(A and B) = P(A) × P(B) for independent events."
        ),
        "example": "Rolling a die: P(even) = 3/6 = 1/2",
    },
    "histogram": {
        "title": "Histograms",
        "explanation": (
            "Histograms display continuous data grouped into class intervals. "
            "y-axis shows frequency density = frequency ÷ class width. "
            "Area of each bar = frequency."
        ),
        "example": "Class 10–15 (width 5), frequency 20 → frequency density = 20/5 = 4",
    },
    "cumulative_frequency": {
        "title": "Cumulative Frequency",
        "explanation": (
            "Running total of frequencies. Plot cumulative frequency against upper class boundary. "
            "Read off: median (50th percentile), LQ (25th), UQ (75th), IQR = UQ − LQ."
        ),
        "example": "n=80: median at 40th value, LQ at 20th, UQ at 60th",
    },
    "scatter_graph": {
        "title": "Scatter Graphs & Correlation",
        "explanation": (
            "Scatter graphs show relationship between two variables. "
            "Positive correlation: both increase together. Negative: one increases, other decreases. "
            "Line of best fit passes through (x̄, ȳ)."
        ),
        "example": "Height vs shoe size: positive correlation",
    },

    # ── Calculus / Advanced ───────────────────────────────────────────────────
    "differentiation": {
        "title": "Differentiation",
        "explanation": (
            "dy/dx gives the gradient of a curve at any point. "
            "Rule: if y = axⁿ, then dy/dx = naxⁿ⁻¹. "
            "Set dy/dx = 0 to find stationary points (maxima/minima)."
        ),
        "example": "y = 3x² + 2x → dy/dx = 6x + 2  |  stationary point: 6x+2=0 → x=−1/3",
    },
    "integration": {
        "title": "Integration",
        "explanation": (
            "The reverse of differentiation. ∫axⁿ dx = axⁿ⁺¹/(n+1) + C. "
            "Definite integral ∫[a,b] f(x)dx gives the area under the curve between x=a and x=b."
        ),
        "example": "∫(3x²)dx = x³ + C  |  ∫₀²(x²)dx = [x³/3]₀² = 8/3",
    },
    "matrix": {
        "title": "Matrices",
        "explanation": (
            "A matrix is a rectangular array of numbers. "
            "Matrix multiplication: (AB)ᵢⱼ = sum of row i of A × column j of B. "
            "Only possible when columns of A = rows of B. Determinant of 2×2: ad−bc."
        ),
        "example": "[[1,2],[3,4]] × [[5],[6]] = [[1×5+2×6],[3×5+4×6]] = [[17],[39]]",
    },
    "loci": {
        "title": "Loci",
        "explanation": (
            "A locus is the set of all points satisfying a given condition. "
            "Common loci: fixed distance from a point (circle), equidistant from two points (perpendicular bisector), "
            "equidistant from two lines (angle bisector)."
        ),
        "example": "Locus of points 3cm from point A = circle centre A, radius 3cm",
    },
    "set_notation": {
        "title": "Set Notation",
        "explanation": (
            "A ∪ B = union (in A or B or both). A ∩ B = intersection (in both). "
            "A' = complement (not in A). n(A) = number of elements in A. "
            "Use Venn diagrams to visualise."
        ),
        "example": "A={1,2,3}, B={2,3,4} → A∪B={1,2,3,4}, A∩B={2,3}",
    },
}

def get_concept(key: str) -> dict | None:
    """Return concept data by key, or None if not found."""
    return MATH_CONCEPTS.get(key.lower())


def list_all_concepts() -> list[str]:
    """Return a sorted list of all concept keys."""
    return sorted(MATH_CONCEPTS.keys())
