"""
O-Level Mathematics Concepts Dictionary
Covers Cambridge IGCSE / O-Level syllabus topics (0580 / 4024)
"""

MATH_CONCEPTS = {
    # ── Number ────────────────────────────────────────────────────────────────
    "addition": {
        "title": "Addition & Fundamental Arithmetic",
        "explanation": (
            "Addition is the fundamental operation of combining quantities. In O-Level mathematics, "
            "this extends to integers, decimals, and fractions. Key properties include the Commutative law "
            "(a + b = b + a) and the Associative law (a + (b + c) = (a + b) + c). "
            "Always ensure alignment of decimal points when performing manual addition."
        ),
        "example": "23.45 + 1.2 = 24.65 | Sum of interior angles in a triangle = 180°.",
    },
    "subtraction": {
        "title": "Subtraction & Differences",
        "explanation": (
            "Subtraction represents the difference between two values or a 'reduction' in quantity. "
            "It is the inverse of addition. In algebraic contexts, subtracting a negative number "
            "is equivalent to adding its positive counterpart: a - (-b) = a + b. "
            "In bearings, subtraction is often used to find 'back bearings' (Heading - 180°)."
        ),
        "example": "85 - 37 = 48 | Temperature drop from 5°C to -2°C: 5 - (-2) = 7°C difference.",
    },
    "multiplication": {
        "title": "Multiplication & Scaling",
        "explanation": (
            "Multiplication is repeated addition or the scaling of a quantity. The result is the 'product'. "
            "Important properties: Multiplicative Identity (a × 1 = a) and the Distributive Law (a(b + c) = ab + ac). "
            "When multiplying decimals, the total number of decimal places in the product equals the sum "
            "of decimal places in the factors."
        ),
        "example": "1.2 × 0.3 = 0.36 | Area of a rectangle = length × width.",
    },
    "division": {
        "title": "Division & Ratios",
        "explanation": (
            "Division is the process of splitting a quantity into equal parts or finding how many times "
            "one number is contained within another. The result is the 'quotient'. "
            "Division by zero is undefined. In O-Level, division is frequently expressed as a fraction: "
            "a ÷ b = a/b."
        ),
        "example": "45 ÷ 9 = 5 | Speed = Distance ÷ Time.",
    },
    "bodmas": {
        "title": "Order of Operations (BODMAS / BIDMAS)",
        "explanation": (
            "Standard priority for evaluating mathematical expressions: "
            "1. Brackets (innermost first) "
            "2. Orders (Indices/Powers/Roots) "
            "3. Division and Multiplication (left to right) "
            "4. Addition and Subtraction (left to right). "
            "Failure to follow BODMAS is a common source of error in multi-step algebra."
        ),
        "example": "10 - 2 × 3 = 10 - 6 = 4. (Incorrect: (10-2) × 3 = 24).",
    },
    "fractions": {
        "title": "Fractions: Proper, Improper & Mixed",
        "explanation": (
            "Fractions denote parts of a whole (Numerator/Denominator). "
            "Proper: Num < Denom; Improper: Num > Denom; Mixed: Integer + Fraction. "
            "To add/subtract: Use a Common Denominator. To multiply: Numerator × Numerator / Denom × Denom. "
            "To divide: Multiply by the Reciprocal (Flip the second fraction)."
        ),
        "example": "2/3 + 1/4 = 8/12 + 3/12 = 11/12 | 2/5 ÷ 4/7 = 2/5 × 7/4 = 14/20 = 7/10.",
    },
    "percentages": {
        "title": "Percentages & Financial Math",
        "explanation": (
            "Percentages represent values as parts per 100. "
            "Percentage Change = (Increase or Decrease / Original Value) × 100. "
            "Reverse Percentages: If a price after a 20% increase is $120, find the original by: "
            "Original = 120 / 1.20 = $100. Do NOT simply subtract 20% from the final price."
        ),
        "example": "15% VAT on $200 = $30. Total = $230.",
    },
    "ratio": {
        "title": "Ratios & Sharing",
        "explanation": (
            "A ratio compares quantities of the same units. To share a quantity in ratio a:b:c: "
            "1. Add the parts (a+b+c) to find the 'total number of shares'. "
            "2. Divide the quantity by the total shares to find the value of 'one share'. "
            "3. Multiply each ratio part by this value."
        ),
        "example": "Share $100 in ratio 2:3. Total parts = 5. One part = $20. Shares = $40 and $60.",
    },
    "proportion": {
        "title": "Proportion (Direct & Inverse)",
        "explanation": (
            "Direct Proportion (y ∝ x): y = kx. As x doubles, y doubles. Graph is a straight line through origin. "
            "Inverse Proportion (y ∝ 1/x): y = k/x. As x doubles, y halves. Graph is a hyperbola. "
            "Solve by first finding the constant of proportionality 'k' using given values."
        ),
        "example": "y ∝ x². If y=12 when x=2, then 12=k(4) → k=3. Rule is y=3x².",
    },
    "hcf": {
        "title": "Highest Common Factor (HCF)",
        "explanation": (
            "The largest integer that divides two or more numbers without a remainder. "
            "Efficient method: Use Prime Factorisation and take the lowest power of all common prime factors."
        ),
        "example": "12 (2² × 3) and 18 (2 × 3²). Common primes are 2 and 3. HCF = 2¹ × 3¹ = 6.",
    },
    "lcm": {
        "title": "Lowest Common Multiple (LCM)",
        "explanation": (
            "The smallest multiple common to two or more numbers. "
            "Efficient method: Use Prime Factorisation and take the highest power of every prime factor "
            "present in at least one number."
        ),
        "example": "12 (2² × 3) and 18 (2 × 3²). Primes are 2 and 3. LCM = 2² × 3² = 36.",
    },
    "prime_factorisation": {
        "title": "Prime Factorisation & Index Notation",
        "explanation": (
            "Expressing a number as a product of prime numbers. Every composite number has a unique "
            "prime factorisation (Fundamental Theorem of Arithmetic). Helpfully used for finding HCF, "
            "LCM, Square Roots, and Cube Roots without a calculator."
        ),
        "example": "120 = 2 × 2 × 2 × 3 × 5 = 2³ × 3¹ × 5¹.",
    },
    "standard_form": {
        "title": "Standard Form (Scientific Notation)",
        "explanation": (
            "Writing numbers in the form A × 10ⁿ, where 1 ≤ A < 10 and n is an integer. "
            "Moving the decimal N places left increases the power n by N. "
            "Moving the decimal N places right decreases the power n by N."
        ),
        "example": "0.00045 = 4.5 × 10⁻⁴ | 7,200,000 = 7.2 × 10⁶.",
    },
    "rounding": {
        "title": "Rounding, Estimation & Bounds",
        "explanation": (
            "Rounding to Decimal Places (d.p.) or Significant Figures (s.f.). "
            "Bounds: If a length L = 5cm correct to the nearest cm, the lower bound (LB) is 4.5 and "
            "the upper bound (UB) is 5.5. Range: 4.5 ≤ L < 5.5."
        ),
        "example": "Round 0.04567 to 2 s.f. → 0.046. (The first s.f. is the first non-zero digit).",
    },
    "square_root": {
        "title": "Powers, Squares & Roots",
        "explanation": (
            "Square numbers are integers raised to the power 2 (1, 4, 9, 16...). "
            "The Square Root (√) is the inverse. Note: √x is always positive in O-Level geometry, "
            "but algebraically x² = 9 implies x = ±3."
        ),
        "example": "√144 = 12 | ∛64 = 4.",
    },
    "indices": {
        "title": "Laws of Indices",
        "explanation": (
            "Rules for manipulating powers: "
            "1. aᵐ × aⁿ = aᵐ⁺ⁿ "
            "2. aᵐ ÷ aⁿ = aᵐ⁻ⁿ "
            "3. (aᵐ)ⁿ = aᵐⁿ "
            "4. a⁻ⁿ = 1/aⁿ "
            "5. a^(1/n) = ⁿ√a "
            "6. a⁰ = 1 (for a≠0)."
        ),
        "example": "25^(1/2) = √25 = 5 | 8^(2/3) = (∛8)² = 2² = 4.",
    },

    # ── Algebra ───────────────────────────────────────────────────────────────
    "expanding_brackets": {
        "title": "Expanding & Simplifying",
        "explanation": (
            "Multiplying terms across parentheses. (a+b)(c+d) = ac + ad + bc + bd. "
            "Special identities: "
            "1. (a+b)² = a² + 2ab + b² "
            "2. (a-b)² = a² - 2ab + b² "
            "3. (a-b)(a+b) = a² - b² (Difference of Two Squares)."
        ),
        "example": "(x+5)(x-5) = x² - 25 | (2x + 3)² = 4x² + 12x + 9.",
    },
    "factorisation": {
        "title": "Factorisation Techniques",
        "explanation": (
            "Method 1: Highest Common Factor (Common term outside). "
            "Method 2: Difference of Two Squares (x² - y² = (x-y)(x+y)). "
            "Method 3: Quadratic Trinomials (Find two numbers that multiply to C and add to B). "
            "Method 4: Grouping (For 4-term expressions)."
        ),
        "example": "x² - 9 = (x-3)(x+3) | x² + 5x + 6 = (x+2)(x+3).",
    },
    "quadratic_formula": {
        "title": "Solving Quadratics (Formula Method)",
        "explanation": (
            "For ax² + bx + c = 0, x = [-b ± √(b² - 4ac)] / 2a. "
            "The discriminant (Δ = b² - 4ac) determines the nature of roots: "
            "Δ > 0: Two distinct real roots. "
            "Δ = 0: One repeated real root. "
            "Δ < 0: No real roots."
        ),
        "example": "x² - 3x + 2 = 0 → x = [3 ± √(9 - 8)]/2 = 2 or 1.",
    },
    "completing_the_square": {
        "title": "Completing the Square",
        "explanation": (
            "Writing x² + bx + c in the form (x + b/2)² - (b/2)² + c. "
            "This is essential for finding the coordinates of the turning point (vertex) of a "
            "quadratic graph. The vertex of y = (x+p)² + q is (-p, q)."
        ),
        "example": "x² + 4x + 7 = (x+2)² - 4 + 7 = (x+2)² + 3. Min point is (-2, 3).",
    },
    "linear_equations": {
        "title": "Linear Equations",
        "explanation": (
            "Solving for an unknown variable by maintaining equality (performing the same operations "
            "on both sides). Always group like terms first. If the unknown is in a fraction, "
            "multiply through by the denominator."
        ),
        "example": "3(x - 4) = 15 → x-4 = 5 → x = 9.",
    },
    "simultaneous_equations": {
        "title": "Simultaneous Equations",
        "explanation": (
            "Finding the unique (x, y) intersection of two lines. "
            "Elimination: Multiply one or both equations to make coefficients of one variable "
            "match, then add or subtract. Substitution: Express x in terms of y from one "
            "equation and plug it into the other."
        ),
        "example": "2x+y=10, x-y=2. Adding them gives 3x=12 → x=4, y=2.",
    },
    "inequalities": {
        "title": "Linear & Graphical Inequalities",
        "explanation": (
            "Solving inequalities is like solving equations, EXCEPT multiplying or dividing by "
            "a negative number reverses the sign (e.g., -2x < 10 becomes x > -5). "
            "On graphs, represent x < k as a dashed line and x ≤ k as a solid line. Shading "
            "identifies the required region."
        ),
        "example": "5 - 2x ≥ 1 → -2x ≥ -4 → x ≤ 2.",
    },
    "algebraic_fractions": {
        "title": "Algebraic Fractions",
        "explanation": (
            "Operations on fractions containing variables. "
            "Simplify by factorising first, then cancelling. "
            "Example: (x²-1)/(x+1) = (x-1)(x+1)/(x+1) = x-1. "
            "When adding, the Common Denominator is usually the product of the denominators."
        ),
        "example": "1/x + 1/(x+1) = (x+1 + x) / x(x+1) = (2x+1) / (x²+x).",
    },
    "sequences": {
        "title": "Number Sequences & nth Term",
        "explanation": (
            "Arithmetic (Linear): Constant difference. nth term = dn + (a-d). "
            "Quadratic: Second difference is constant. nth term = an² + bn + c. "
            "Geometric: Constant ratio. Powers of n. "
            "To find nth term of a linear sequence, find the difference 'd' and adjust for term 1."
        ),
        "example": "5, 8, 11, 14... Diff=3. nth term = 3n + 2.",
    },
    "functions": {
        "title": "Functions & Inverse Functions",
        "explanation": (
            "Notation f(x) or f: x → ... "
            "To find the inverse f⁻¹(x): "
            "1. Let y = f(x). "
            "2. Rearrange the equation to make x the subject. "
            "3. Replace x with f⁻¹(x) and y with x. "
            "Composite function fg(x) means f(g(x)) — solve inside-out."
        ),
        "example": "f(x)=3x-1. Find f⁻¹. y=3x-1 → x=(y+1)/3 → f⁻¹(x)=(x+1)/3.",
    },

    # ── Geometry ──────────────────────────────────────────────────────────────
    "area": {
        "title": "Area of 2D Shapes",
        "explanation": (
            "Rectangle: L × W | Triangle: ½ × B × H | Circle: πr² | Trapezium: ½(a+b)h. "
            "Parallelogram: B × H. Sector of circle: (θ/360) × πr². "
            "Remember that H must be the perpendicular height, not the slant length."
        ),
        "example": "Trapezium with parallel sides 5, 9 and height 4: Area = ½(14)4 = 28.",
    },
    "perimeter": {
        "title": "Perimeter & Circumference",
        "explanation": (
            "The total distance around the boundary. Circumference = 2πr or πd. "
            "Arc Length of a sector = (θ/360) × 2πr. "
            "Perimeter of a sector = Arc Length + 2r. (Don't forget the radii!)."
        ),
        "example": "Circumference of a 10cm diameter circle = 10π ≈ 31.4cm.",
    },
    "volume": {
        "title": "Volume & Surface Area (3D)",
        "explanation": (
            "Prism: Cross-section Area × Length. Cylinder: πr²h. "
            "Pyramid: ⅓ × Base Area × H. Cone: ⅓πr²h. Sphere: 4/3πr³. "
            "Total Surface Area includes faces (e.g. Cylinder = 2πr² + 2πrh)."
        ),
        "example": "Volume of sphere radius 3: 4/3 × π × 27 = 36π ≈ 113.1.",
    },
    "pythagoras": {
        "title": "Pythagoras' Theorem",
        "explanation": (
            "In any right-angled triangle, a² + b² = c², where c is the hypotenuse. "
            "To find c: √(a² + b²). To find a: √(c² - b²). "
            "Also applies in 3D: Diagonal² = L² + W² + H²."
        ),
        "example": "Sides 5 and 12: Hypotenuse = √(25 + 144) = √169 = 13.",
    },
    "angles": {
        "title": "Angle Geometry Rules",
        "explanation": (
            "1. Angles on a line = 180°. "
            "2. Angles at a point = 360°. "
            "3. Vertically opposite angles are equal. "
            "4. Triangle sum = 180°; Quadrilateral sum = 360°. "
            "5. Sum of exterior angles in any polygon = 360°. "
            "6. Sum of interior angles = (n-2) × 180°."
        ),
        "example": "Regular Hexagon: Interior sum = 4 × 180 = 720°. Each angle = 120°.",
    },
    "parallel_lines": {
        "title": "Parallel Lines (F, Z, C Angles)",
        "explanation": (
            "When parallel lines are cut by a transversal: "
            "- Alternate angles are equal (Z-shape). "
            "- Corresponding angles are equal (F-shape). "
            "- Co-interior (Allied) angles sum to 180° (C-shape)."
        ),
        "example": "If angle A and B are alternate on parallel lines, A = B.",
    },
    "circle_theorems": {
        "title": "Circle Theorems",
        "explanation": (
            "1. Angle at center is twice angle at circumference. "
            "2. Angle in a semicircle is 90°. "
            "3. Angles in same segment are equal. "
            "4. Opposite angles of cyclic quadrilateral sum to 180°. "
            "5. Angle between tangent and radius is 90°. "
            "6. Tangents from an external point are equal in length."
        ),
        "example": "Opposite angles of a cyclic quad are 70° and x. x = 110°.",
    },
    "similarity": {
        "title": "Similarity (Lengths, Areas, Volumes)",
        "explanation": (
            "Two shapes are similar if they have the same shape but different size (proportional). "
            "If Length ratio = L₁:L₂ (scale factor k), then: "
            "Area ratio = k². Volume ratio = k³. "
            "This is a frequent O-Level paper question."
        ),
        "example": "Scale factor 3. Area of small = 10. Area of large = 10 × 3² = 90.",
    },
    "congruence": {
        "title": "Congruent Triangles",
        "explanation": (
            "Condition for two triangles to be identical (congruent): "
            "SSS (3 sides), SAS (2 sides, included angle), ASA (2 angles, included side), "
            "AAs (2 angles, matching side), RHS (Right-angle, Hypotenuse, Side)."
        ),
        "example": "Two triangles with sides 6, 8, 10 are congruent by SSS.",
    },
    "transformations": {
        "title": "Transformations",
        "explanation": (
            "1. Reflection: Need 'Mirror Line' (e.g., y=x). "
            "2. Rotation: Need 'Center', 'Angle', and 'Direction' (e.g., (0,0), 90°, CLOCKWISE). "
            "3. Translation: Need 'Column Vector' (x/y). "
            "4. Enlargement: Need 'Center' and 'Scale Factor'. (Negative factor flips and scales)."
        ),
        "example": "Enlargement SF -2 center (0,0) doubles size and rotates 180°.",
    },
    "vectors": {
        "title": "Vectors (Column & Geometric)",
        "explanation": (
            "A quantity with magnitude and direction. AB = OB - OA (Position vectors). "
            "Column vectors: (x / y). Multiple of vector: k(x / y) = (kx / ky). "
            "Magnitude |v| = √(x² + y²). Resultant vector is the sum of vectors."
        ),
        "example": "a = (3/4), b = (1/-2) → a + b = (4/2).",
    },

    # ── Trigonometry ──────────────────────────────────────────────────────────
    "trigonometry": {
        "title": "Trigonometry (SOH-CAH-TOA)",
        "explanation": (
            "Definitions for right-angled triangles: "
            "Sin θ = Opp/Hyp | Cos θ = Adj/Hyp | Tan θ = Opp/Adj. "
            "To find angle θ, use inverse functions: θ = sin⁻¹(Ratio). "
            "Always check if your calculator is in 'DEG' (degrees) mode."
        ),
        "example": "Adj=4, Hyp=5 → cos θ = 4/5 = 0.8 → θ = 36.9°.",
    },
    "sine_rule": {
        "title": "Sine Rule (Non-Right Triangles)",
        "explanation": (
            "a/sinA = b/sinB = c/sinC. "
            "Use when you know: "
            "1. Two angles and any side. "
            "2. Two sides and a non-included angle (Beware of the ambiguous case!)."
        ),
        "example": "Side a=10, angle A=30°, angle B=45° → b = 10 sin 45 / sin 30 = 14.1.",
    },
    "cosine_rule": {
        "title": "Cosine Rule (Non-Right Triangles)",
        "explanation": (
            "Side: a² = b² + c² - 2bc cosA. "
            "Angle: cosA = (b² + c² - a²) / 2bc. "
            "Use when you know: "
            "1. Three sides (SSS). "
            "2. Two sides and the included angle (SAS)."
        ),
        "example": "a=5, b=6, angle C=60° → c² = 25 + 36 - 2(30)(0.5) = 31. c = √31.",
    },
    "bearing": {
        "title": "Bearings",
        "explanation": (
            "Directional measurements in O-Level: "
            "1. Measured from North. "
            "2. Measured CLOCKWISE. "
            "3. Always THREE digits (e.g., 045° instead of 45°). "
            "Back Bearing = Bearing ± 180°."
        ),
        "example": "The bearing of B from A is 070°. The bearing of A from B is 250°.",
    },

    # ── Graphs ────────────────────────────────────────────────────────────────
    "gradient": {
        "title": "Gradient (m)",
        "explanation": (
            "Slope = (Change in y) / (Change in x) = (y₂ - y₁) / (x₂ - x₁). "
            "Horizontal lines m=0. Vertical lines m is undefined. "
            "Parallel lines have the same gradient. Perpendicular lines have gradients m₁m₂ = -1."
        ),
        "example": "Points (0,0) and (2,6) → m = 6/2 = 3.",
    },
    "y_intercept": {
        "title": "y-Intercept (c)",
        "explanation": (
            "The coordinate where the line crosses the y-axis (where x=0). "
            "In the form y = mx + c, the constant term 'c' is the y-intercept. "
            "In a practical graph (e.g. Distance-Time), this is often the starting value."
        ),
        "example": "y = 4x - 7 crosses the y-axis at (0, -7).",
    },
    "straight_line_graph": {
        "title": "Straight Line Graphs",
        "explanation": (
            "Standard form: y = mx + c. "
            "To plot: Calculate 3 points, or plot 'c' and use 'm' (rise/run). "
            "General form: Ax + By = D (can be rearranged to y = mx + c)."
        ),
        "example": "2x + y = 5 → y = -2x + 5. Gradient = -2, y-intercept = 5.",
    },
    "quadratic_graph": {
        "title": "Quadratic Graphs (Parabolas)",
        "explanation": (
            "Shape: Parabola. "
            "If a > 0: 'Happy' face (Minimum point). "
            "If a < 0: 'Sad' face (Maximum point). "
            "The graph is symmetrical. The line of symmetry is x = -b/2a."
        ),
        "example": "y = x² + 2. Minimum point is (0,2). Symmetrical about y-axis.",
    },
    "distance_time_graph": {
        "title": "Distance and Speed-Time Graphs",
        "explanation": (
            "Distance-Time: Gradient = Speed. Horizontal = Stationary. "
            "Speed-Time: Gradient = Acceleration. Area under graph = Distance travelled. "
            "Units must be consistent (e.g., m/s² for acceleration)."
        ),
        "example": "Area of a triangle shape on Speed-Time = ½ × base × peak speed.",
    },

    # ── Statistics ────────────────────────────────────────────────────────────
    "mean": {
        "title": "Mean (Average)",
        "explanation": (
            "Mean = Σx / n. For grouped frequency: Mean = Σ(fx) / Σf. "
            "It is the most representative average but is sensitive to 'outliers' (extreme values)."
        ),
        "example": "Data: 2, 8, 11. Mean = (2+8+11)/3 = 7.",
    },
    "median": {
        "title": "Median (Middle Value)",
        "explanation": (
            "The middle value of a sorted data set. Position = (n+1)/2. "
            "If n is even, average the two middle values. "
            "Median is useful because it is not affected by outliers."
        ),
        "example": "2, 5, 8, 12, 19. Median = 8. (Middle of 5 numbers).",
    },
    "mode": {
        "title": "Mode (Most Frequent)",
        "explanation": (
            "The value that appears most often. In grouped data, we look for the 'Modal Class'. "
            "A set can be bimodal if two values appear with the same highest frequency."
        ),
        "example": "Data: 2, 3, 3, 4, 5. Mode = 3.",
    },
    "range": {
        "title": "Range & Spread",
        "explanation": (
            "Range = Highest Value - Lowest Value. "
            "It is a simple measure of dispersion. Interquartile Range (IQR) = UQ - LQ is often "
            "more useful in O-Level as it ignores extreme values."
        ),
        "example": "Scores: 10, 45, 48, 50. Range = 40.",
    },
    "probability": {
        "title": "Probability",
        "explanation": (
            "P(A) = Favorable Outcomes / Total Outcomes. "
            "0 ≤ P(A) ≤ 1. (0 = Impossible, 1 = Certain). "
            "Mutually exclusive: P(A or B) = P(A) + P(B). "
            "Independent events: P(A and B) = P(A) × P(B)."
        ),
        "example": "Rolling a 6 and flipping Heads: 1/6 × 1/2 = 1/12.",
    },
    "histogram": {
        "title": "Histograms",
        "explanation": (
            "Unlike bar charts, histograms handle continuous data with unequal class widths. "
            "Frequency Density = Frequency / Class Width. "
            "The AREA of the bar represents the frequency. Always check the y-axis label."
        ),
        "example": "Class width 10, Frequency 50 → Freq Density = 5.",
    },
    "cumulative_frequency": {
        "title": "Cumulative Frequency",
        "explanation": (
            "A running total of frequency. Plot points at the UPPER BOUND of each class. "
            "Used to estimate: "
            "- Median (50% of n) "
            "- Lower Quartile (25% of n) "
            "- Upper Quartile (75% of n) "
            "- Percentiles."
        ),
        "example": "If total n=120, median is read from CF=60 on the y-axis.",
    },
    "scatter_graph": {
        "title": "Scatter Graphs & Correlation",
        "explanation": (
            "Show the relationship between two variables. "
            "Positive Correlation: Both increase. "
            "Negative Correlation: One increases, other decreases. "
            "No Correlation: Random points. "
            "Line of Best Fit: A straight line that passes through the 'center' of points."
        ),
        "example": "Correlation between height and weight is usually positive.",
    },

    # ── Calculus / Advanced ───────────────────────────────────────────────────
    "differentiation": {
        "title": "Differentiation (Gradient functions)",
        "explanation": (
            "Calculates the rate of change. If y = xⁿ, then dy/dx = nxⁿ⁻¹. "
            "Used to: "
            "1. Find the gradient of a curve at a specific x. "
            "2. Find Turning Points (where dy/dx = 0)."
        ),
        "example": "y = x³ + 5x → dy/dx = 3x² + 5.",
    },
    "integration": {
        "title": "Integration (Area Under Curve)",
        "explanation": (
            "The inverse of differentiation. ∫xⁿ dx = (xⁿ⁺¹)/(n+1) + C. "
            "The '+ C' is the 'constant of integration'. "
            "Definite integrals are used to calculate the exact area bound by a curve and an axis."
        ),
        "example": "∫(2x + 3)dx = x² + 3x + C.",
    },
    "matrix": {
        "title": "Matrices",
        "explanation": (
            "Rectangular arrays of numbers. "
            "Addition/Subtraction: Corresponding elements. "
            "Multiplication: Row × Column. "
            "Determinant |A| of (a b / c d) = ad - bc. "
            "Inverse exists only if |A| ≠ 0."
        ),
        "example": "Inverse A = (1/|A|) × (d -b / -c a).",
    },
    "loci": {
        "title": "Loci & Constructions",
        "explanation": (
            "Locus of points satisfying a condition: "
            "- From a point: Circle. "
            "- From 2 points: Perpendicular Bisector. "
            "- From 2 lines: Angle Bisector. "
            "- From 1 line: Parallel lines on either side."
        ),
        "example": "Construction of a scale map requires precise loci.",
    },
    "set_notation": {
        "title": "Sets & Venn Diagrams",
        "explanation": (
            "∈: 'is an element of' | ∩: Intersection (AND) | ∪: Union (OR) | ξ: Universal Set. "
            "A': Complement (elements not in A). "
            "n(A): Number of elements. "
            "Empty Set (∅): Set with zero elements."
        ),
        "example": "A ∩ B is the overlapping middle part of the circles.",
    },
}

def get_concept(key: str) -> dict | None:
    """Return concept data by key, or None if not found."""
    return MATH_CONCEPTS.get(key.lower())


def list_all_concepts() -> list[str]:
    """Return a sorted list of all concept keys."""
    return sorted(MATH_CONCEPTS.keys())
