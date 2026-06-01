
#include <math.h>


#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT
#endif


EXPORT float calc_bmi(float weight_kg, float height_m) {
    return weight_kg / (height_m * height_m);
}


EXPORT int bmi_category(float bmi) {
    if (bmi < 18.5f) return 0;
    if (bmi < 25.0f) return 1;
    if (bmi < 30.0f) return 2;
    if (bmi < 35.0f) return 3;
    if (bmi < 40.0f) return 4;
    return 5;
}


EXPORT float calories_burned(float weight_kg, float met, int minutes) {
    float hours = (float)minutes / 60.0f;
    return met * weight_kg * hours;
}


EXPORT float met_for_activity_ext(float *met_table, int table_size,
                                   int type_id, float intensity) {
    return met_table[type_id] * intensity;
}


EXPORT void calc_bmi_batch(float *w, float *h, float *out, int n) {
    for (int i = 0; i < n; i++) {
        out[i] = calc_bmi(w[i], h[i]);
    }
}

EXPORT void calories_batch(float *w, float *met, int *mins, float *out, int n) {
    for (int i = 0; i < n; i++) {
        out[i] = calories_burned(w[i], met[i], mins[i]);
    }
}
