using System;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Projet2;

public partial class ProfileForm : Form
{
    private readonly ApiClient _apiClient = new ApiClient();
    private int? _userId;

    // Le constructeur accepte l'ID de l'utilisateur (null si c'est un nouveau)
    public ProfileForm(int? userId)
    {
        InitializeComponent();
        _userId = userId;

        this.Load += ProfileForm_Load;
        this.btnSave.Click += BtnSave_Click;
        this.btnBack.Click += BtnBack_Click;
    }

    private async void ProfileForm_Load(object sender, EventArgs e)
    {
        if (_userId.HasValue)
        {
            // Mode Édition : on charge les données depuis l'API
            User user = await _apiClient.GetUserAsync(_userId.Value);
            if (user != null)
            {
                txtName.Text = user.Name;
                numWeight.Value = (decimal)user.WeightKg;
                numHeight.Value = (decimal)user.HeightM;
                if (user.Age.HasValue) numAge.Value = user.Age.Value;
                if (!string.IsNullOrEmpty(user.Sex)) cbSex.Text = user.Sex;
                
                UpdateBmiDisplay(user.Bmi, user.BmiCategory);
            }
        }
        else
        {
            // Mode Création : valeurs par défaut
            numWeight.Value = 70;
            numHeight.Value = 1.70m;
            numAge.Value = 25;
            cbSex.SelectedIndex = 0; // 'M' par défaut
        }
    }

    private async void BtnSave_Click(object sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(txtName.Text))
        {
            MessageBox.Show("Le nom est obligatoire.", "Erreur", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        // Création d'un objet anonyme correspondant au format attendu par Flask
        var userData = new
        {
            name = txtName.Text,
            weight_kg = (float)numWeight.Value,
            height_m = (float)numHeight.Value,
            age = (int)numAge.Value,
            sex = cbSex.Text
        };

        try
        {
            User updatedUser;

            if (_userId.HasValue)
            {
                // Mise à jour (PUT)
                updatedUser = await _apiClient.UpdateUserAsync(_userId.Value, userData);
            }
            else
            {
                // Création (POST)
                updatedUser = await _apiClient.CreateUserAsync(userData);
                if (updatedUser != null)
                {
                    _userId = updatedUser.Id; // On mémorise le nouvel ID
                }
            }

            if (updatedUser != null)
            {
                // Affichage IMC "live" grâce à la réponse du serveur !
                UpdateBmiDisplay(updatedUser.Bmi, updatedUser.BmiCategory);
                MessageBox.Show("Profil enregistré avec succès !", "Succès", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Erreur lors de la sauvegarde : {ex.Message}", "Erreur", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void UpdateBmiDisplay(float bmi, string category)
    {
        lblBmiValue.Text = bmi.ToString("F1");
        lblBmiCategory.Text = category;
    }

    private void BtnBack_Click(object sender, EventArgs e)
    {
        var menu = new MenuForm(_userId.Value);
        menu.Show();
        this.Close();
    }
}