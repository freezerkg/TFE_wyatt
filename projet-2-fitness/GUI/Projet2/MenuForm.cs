using System;
using System.Windows.Forms;

namespace Projet2
{
    public partial class MenuForm : Form
    {
        private readonly int _userId;

        public MenuForm(int userId)
        {
            InitializeComponent();
            _userId = userId;
        }

        private void btnModifierProfil_Click(object sender, EventArgs e)
        {
            var profile = new ProfileForm(_userId);
            profile.Show();
            this.Hide();
        }

        private void btnAjoutSeance_Click(object sender, EventArgs e)
        {
            var session = new AddSessionForm(_userId);
            session.ShowDialog(); 
        }

        private void btnBack_Click(object sender, EventArgs e)
        {
            new LoginForm().Show();
            this.Close();
        }
    }
}