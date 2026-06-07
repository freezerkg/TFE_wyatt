using System;
using System.Windows.Forms;

namespace Projet2
{
    public partial class AddSessionForm : Form
    {
        private readonly ApiClient _apiClient = new ApiClient();
        private readonly int _userId;

        public AddSessionForm(int userId)
        {
            InitializeComponent();
            _userId = userId;
            LoadActivites();
        }

        private async void LoadActivites()
        {
            var activites = await _apiClient.GetActivitesAsync();
            cbActivite.DataSource = activites;
            cbActivite.DisplayMember = "Nom";
        }

        private async void BtnSave_Click(object sender, EventArgs e)
        {
            if (numDuration.Value <= 0)
            {
                MessageBox.Show("La durée doit être supérieure à 0 !");
                return;
            }

            var selected = (Activite)cbActivite.SelectedItem;
            
            // CORRECTION : On envoie les données attendues par app.py
            var data = new { 
                user_id = _userId,
                activite_id = selected.Id,
                duration_min = (int)numDuration.Value,
                date = DateTime.Now.ToString("yyyy-MM-dd")
            };

            var session = await _apiClient.CreateSessionAsync(data);
    
            if (session != null)
            {
                MessageBox.Show("Séance enregistrée !");
                this.Close();
            }
        }

        private void numDuration_ValueChanged(object sender, EventArgs e)
        {}
    }
}