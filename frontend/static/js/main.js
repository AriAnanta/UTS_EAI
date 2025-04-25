// main.js - JavaScript untuk Sistem Manajemen Hotel

document.addEventListener("DOMContentLoaded", function () {
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  var flashMessages = document.querySelectorAll(".alert-dismissible");
  flashMessages.forEach(function (flashMessage) {
    setTimeout(function () {
      var closeButton = new bootstrap.Alert(flashMessage);
      closeButton.close();
    }, 5000); 
  });

  var dateInputs = document.querySelectorAll('input[type="date"]');
  dateInputs.forEach(function (input) {
    if (!input.value && !input.hasAttribute("data-no-default")) {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, "0");
      const day = String(today.getDate()).padStart(2, "0");
      input.value = `${year}-${month}-${day}`;
    }

    if (!input.hasAttribute("min") && !input.hasAttribute("data-no-min")) {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, "0");
      const day = String(today.getDate()).padStart(2, "0");
      input.setAttribute("min", `${year}-${month}-${day}`);
    }
  });

  var forms = document.querySelectorAll(".needs-validation");
  Array.prototype.slice.call(forms).forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });

  if (document.getElementById("booking-form")) {
    const checkInInput = document.getElementById("check_in");
    const checkOutInput = document.getElementById("check_out");
    const roomTypeSelect = document.getElementById("room_type_code");
    const durationOutput = document.getElementById("duration");
    const totalPriceOutput = document.getElementById("total_price");

    const updateBookingCalculations = function () {
      if (checkInInput.value && checkOutInput.value && roomTypeSelect.value) {
        // Hitung durasi
        const checkIn = new Date(checkInInput.value);
        const checkOut = new Date(checkOutInput.value);
        const diffTime = Math.abs(checkOut - checkIn);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        // Tampilkan durasi
        if (diffDays > 0) {
          durationOutput.textContent = `${diffDays} malam`;

          // Ambil harga kamar dari data-price
          const selectedOption =
            roomTypeSelect.options[roomTypeSelect.selectedIndex];
          const pricePerNight = parseFloat(
            selectedOption.getAttribute("data-price") || "0"
          );

          // Hitung dan tampilkan total harga
          if (pricePerNight > 0) {
            const totalPrice = diffDays * pricePerNight;
            totalPriceOutput.textContent = `Rp ${totalPrice.toLocaleString(
              "id-ID"
            )}`;
          } else {
            totalPriceOutput.textContent = "Harga tidak tersedia";
          }
        } else {
          durationOutput.textContent = "Tanggal tidak valid";
          totalPriceOutput.textContent = "-";
        }
      } else {
        durationOutput.textContent = "-";
        totalPriceOutput.textContent = "-";
      }
    };

    if (checkInInput)
      checkInInput.addEventListener("change", updateBookingCalculations);
    if (checkOutInput)
      checkOutInput.addEventListener("change", updateBookingCalculations);
    if (roomTypeSelect)
      roomTypeSelect.addEventListener("change", updateBookingCalculations);
  }

  // Konfirmasi untuk aksi hapus
  var deleteButtons = document.querySelectorAll(".btn-delete");
  deleteButtons.forEach(function (button) {
    button.addEventListener("click", function (e) {
      if (!confirm("Apakah Anda yakin ingin menghapus item ini?")) {
        e.preventDefault();
      }
    });
  });

  // Konfirmasi untuk aksi pembatalan booking
  var cancelButtons = document.querySelectorAll(".btn-cancel-booking");
  cancelButtons.forEach(function (button) {
    button.addEventListener("click", function (e) {
      if (!confirm("Apakah Anda yakin ingin membatalkan booking ini?")) {
        e.preventDefault();
      }
    });
  });

  // Format nomor sebagai mata uang
  var currencyElements = document.querySelectorAll(".currency");
  currencyElements.forEach(function (el) {
    const value = parseFloat(el.textContent.trim());
    if (!isNaN(value)) {
      el.textContent = `Rp ${value.toLocaleString("id-ID")}`;
    }
  });

  // Filter tabel 
  const tableFilter = document.getElementById("table-filter");
  if (tableFilter) {
    tableFilter.addEventListener("input", function () {
      const filterValue = this.value.toLowerCase();
      const table = document.querySelector(this.getAttribute("data-table"));
      const rows = table.querySelectorAll("tbody tr");

      rows.forEach(function (row) {
        const text = row.textContent.toLowerCase();
        if (text.indexOf(filterValue) > -1) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  }

  const urlParams = new URLSearchParams(window.location.search);
  const modalParam = urlParams.get("modal");
  if (modalParam) {
    const modalElement = document.getElementById(modalParam);
    if (modalElement) {
      const modal = new bootstrap.Modal(modalElement);
      modal.show();
    }
  }
});
