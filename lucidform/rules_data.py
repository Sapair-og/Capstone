"""Static reference data for deterministic rules ("Validation Rules DB" in the workflow diagram)."""

STATES = (
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
)

_NE = ("Arunachal Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Tripura", "Assam")

# India Post: first two digits of a PIN identify the postal circle. Coarse by design — a prefix may
# cover several states, so this rule only rejects pairs that are impossible, never ones that are unusual.
_PREFIX: dict[str, tuple[str, ...]] = {
    "11": ("Delhi",), "12": ("Haryana",), "13": ("Haryana", "Punjab"), "14": ("Punjab",), "15": ("Punjab",),
    "16": ("Punjab", "Chandigarh", "Haryana"), "17": ("Himachal Pradesh",), "18": ("Jammu and Kashmir",),
    "19": ("Jammu and Kashmir", "Ladakh"), "24": ("Uttar Pradesh", "Uttarakhand"),
    "26": ("Uttar Pradesh", "Uttarakhand"), "36": ("Gujarat", "Dadra and Nagar Haveli and Daman and Diu"),
    "39": ("Gujarat", "Dadra and Nagar Haveli and Daman and Diu"), "40": ("Maharashtra", "Goa"),
    "49": ("Chhattisgarh",), "50": ("Telangana", "Andhra Pradesh"), "51": ("Andhra Pradesh", "Telangana"),
    "60": ("Tamil Nadu", "Puducherry"), "67": ("Kerala", "Puducherry"), "68": ("Kerala", "Lakshadweep"),
    "73": ("West Bengal", "Sikkim"), "74": ("West Bengal", "Andaman and Nicobar Islands"), "78": ("Assam",),
    "79": _NE, "80": ("Bihar",), "81": ("Jharkhand", "Bihar"), "82": ("Jharkhand", "Bihar"),
    "83": ("Jharkhand",), "84": ("Bihar",), "85": ("Bihar",),
}
for _p, _s in {**{k: "Uttar Pradesh" for k in ("20", "21", "22", "23", "25", "27", "28")},
               **{k: "Rajasthan" for k in ("30", "31", "32", "33", "34")},
               **{k: "Gujarat" for k in ("37", "38")},
               **{k: "Maharashtra" for k in ("41", "42", "43", "44")},
               **{k: "Madhya Pradesh" for k in ("45", "46", "47", "48")},
               **{k: "Andhra Pradesh" for k in ("52", "53")},
               **{k: "Karnataka" for k in ("56", "57", "58", "59")},
               **{k: "Tamil Nadu" for k in ("61", "62", "63", "64")},
               **{k: "Kerala" for k in ("69",)},
               **{k: "West Bengal" for k in ("70", "71", "72")},
               **{k: "Odisha" for k in ("75", "76", "77")}}.items():
    _PREFIX[_p] = (_s,)


def states_for_pincode(pin: str) -> tuple[str, ...]:
    return _PREFIX.get(pin[:2], ())
